import importlib
import logging
import os
import shutil

import pytest

from mattapi.api.keyboard.keyboard_util import check_keyboard_state
from mattapi.api.os_helpers import OSHelper
from mattapi.configuration.config_parser import validate_config_ini
from mattapi.control_center.commands import delete
from mattapi.util.arg_parser import get_core_args, set_core_arg
from mattapi.util.cleanup import *
from mattapi.util.logger_manager import initialize_logger
from mattapi.util.path_manager import PathManager
from mattapi.util.system import check_7zip, fix_terminal_encoding, init_tesseract_path, reset_terminal_encoding
from mattapi.util.target_loader import collect_tests
from mattapi.scripts.main import set_code_paths


logger = logging.getLogger(__name__)


def test():
    logger.error ('hello world')


def main():
    args = get_core_args()
    set_code_paths(args)
    if args.control:
        exit_iris('Can\'t use Control Center with lite command, exiting Iris.', 1)
    else:
        initialize_logger()
        validate_config_ini(args)
        if verify_config(args):
            pytest_args = None
            settings = None
            try:
                if pytest_args is None:
                    pytest_args = get_test_params()
                if len(pytest_args) == 0:
                    exit_iris('No tests found.', status=1)

                pytest_args.append('-vs')
                pytest_args.append('-r ')
                pytest_args.append('-s')
                target_plugin = get_target(args.target)
                if settings is not None:
                    logger.debug('Passing settings to target: %s' % settings)
                    target_plugin.update_settings(settings)
                initialize_platform(args)
                pytest.main(pytest_args, plugins=[target_plugin])
            except ImportError as e:
                exit_iris('Could not load plugin for %s target, error: %s' % (args.target, e), status=1)
        else:
            exit_iris('Failed platform verification.', status=1)


def get_target(target_name):
    logger.info('Desired target: %s' % target_name)
    logger.info('Desired module: targets.%s.main' %  target_name)
    try:
        my_module = importlib.import_module('targets.%s.main' % target_name)
        logger.info('Successful import!')
        try:
            target_plugin = my_module.Target()
            logger.info('Found target named %s' % target_plugin.target_name)
            return target_plugin
        except NameError:
            exit_iris('Can\'t find default Target class.', status=1)
    except ImportError as e:
        if e.name.__contains__('Xlib') and not OSHelper.is_linux():
            pass
        else:
            exit_iris('Problems importing module:\n%s' % e, status=1)


def initialize_platform(args):
    init()
    fix_terminal_encoding()
    PathManager.create_working_directory(args.workdir)
    PathManager.create_run_directory()


def get_test_params():
    pytest_args = []
    if get_core_args().rerun:
        failed_tests_file = os.path.join(PathManager.get_working_dir(), 'lastfail.txt')
        tests_dir = os.path.join(PathManager.get_tests_dir(), get_core_args().target)
        failed_tests = []
        with open(failed_tests_file, 'r') as f:
            for line in f:
                failed_tests.append(line.rstrip('\n'))
        f.close()
        # Read first line to see if these tests apply to current target.
        if tests_dir in failed_tests[0]:
            pytest_args = failed_tests
        else:
            logging.error('The -a flag cannot be used now because the last failed tests don\'t match current target.')
    else:
        tests_to_execute = collect_tests()
        if len(tests_to_execute) > 0:
            for running in tests_to_execute:
                pytest_args.append(running)
        else:
            exit_iris('No tests to execute.', status=1)
    return pytest_args


def verify_config(args):
    """Checks keyboard state is correct, and that Tesseract and 7zip are installed."""
    try:
        if not all([check_keyboard_state(args.no_check), init_tesseract_path(), check_7zip()]):
            exit_iris('Failed platform check, closing Iris.', status=1)
    except KeyboardInterrupt as e:
        exit_iris(e, status=1)
    return True


def exit_iris(message, status=0):
    if status == 0:
        logger.info(message)
    elif status == 1:
        logger.error(message)
    else:
        logger.debug(message)
    delete(PathManager.get_run_id(), update_run_file=False)
    ShutdownTasks.at_exit()
    exit(status)


class ShutdownTasks(CleanUp):
    """Class for restoring system state when Iris has been quit.
    """

    @staticmethod
    def at_exit():
        reset_terminal_encoding()

        if os.path.exists(PathManager.get_temp_dir()):
            shutil.rmtree(PathManager.get_temp_dir(), ignore_errors=True)
