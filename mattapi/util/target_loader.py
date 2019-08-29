# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import importlib
import logging
import os
import sys

from mattapi.api.os_helpers import OSHelper
from mattapi.api.settings import Settings
from mattapi.util.arg_parser import get_core_args
from mattapi.util.path_manager import PathManager

logger = logging.getLogger(__name__)
core_args = get_core_args()


def check_target(target: str = None):
    """Checks if provided target exists."""
    # Currently not in use, but maintaining for possible future use.

    if target is None:
        logger.warning('No target provided.')

    local_target_path = os.path.join(PathManager.get_module_dir(), 'targets')
    package_target_path = os.path.join(PathManager.get_module_dir(), 'mattapi', 'targets')

    if os.path.exists(os.path.join(local_target_path, target)):
        return True
    if os.path.exists(os.path.join(package_target_path, target)):
        return True

    target_list = []
    local_path_exists = os.path.exists(local_target_path)
    package_path_exists = os.path.exists(package_target_path)

    if local_path_exists:
        target_list += scan_dir(local_target_path)

    if package_path_exists:
        target_list += scan_dir(package_target_path)

    if not local_path_exists and not package_path_exists:
        path_warning(local_target_path)
    else:
        logger.critical('Target %s doesn\'t exist.')
        logger.critical('Did you mean to choose one of these instead?')
        for target in target_list:
            logger.critical('\t%s' % target)

    return False


def scan_dir(path):
    target_list = [f.path for f in os.scandir(path) if f.is_dir()]
    target_names = []

    for idx, target in enumerate(target_list):
        if 'pycache' not in target:
            target_names.append(os.path.basename(os.path.normpath(target)))

    return target_names



def get_target(target_name: str):
    logger.info('Desired target: %s' % target_name)
    logger.info('Desired module: targets.%s.main' %  target_name)
    try:
        logger.debug('Attempt to load target from default package root.')
        target = import_package_by_name(target_name, os.path.join(Settings.PACKAGE_ROOT, 'mattapi'))
        return target
    except Exception as e:
        logger.error(e)
        logger.debug('Attempt to load target from code root.')
        target = import_package_by_name(target_name, Settings.CODE_ROOT)
        return target


def import_package_by_name(target_name: str, path: str):
    sys.path.append(path)
    logger.debug('Looking for %s in path %s' % (target_name, path))
    try:
        my_module = importlib.import_module('targets.%s.main' % target_name)
        logger.info('Successful import!')
        try:
            target_plugin = my_module.Target()
            logger.info('Found target named %s' % target_plugin.target_name)
            return target_plugin
        except NameError:
            raise Exception('Target %s not found in path %s' % (target_name, path))
    except ImportError as e:
        if e.name.__contains__('Xlib') and not OSHelper.is_linux():
            pass
        else:
            logger.error('Problems importing module:\n%s' % e)
            raise ImportError


def collect_tests():
    """Collects tests based on include/exclude criteria and selected target."""
    target = core_args.target
    test_list = []

    include = core_args.test
    exclude = core_args.exclude
    if os.path.isfile(include):
        with open(include, 'r') as f:
            for line in f:
                test_list.append(line.rstrip('\n'))
        f.close()
    else:
        tests_dir = os.path.join(PathManager.get_tests_dir(), target)
        if not os.path.exists(tests_dir):
            path_warning(tests_dir)
            return test_list

        logger.debug('Path %s found. Checking content ...', tests_dir)
        for dir_path, sub_dirs, all_files in PathManager.sorted_walk(tests_dir):
            for current_file in all_files:
                directory = '%s%s%s' % (os.sep, core_args.directory, os.sep)
                include_params = [include]
                exclude_params = [exclude]
                if ',' in include:
                    include_params = include.split(',')
                if ',' in exclude:
                    exclude_params = exclude.split(',')
                current_full_path = os.path.join(dir_path, current_file)
                if current_file.endswith('.py') and not current_file.startswith('__'):
                    if include is '' and exclude is '' and directory is '':
                        if not current_full_path in test_list:
                            test_list.append(current_full_path)
                    else:
                        if core_args.directory is '' or directory in current_full_path:
                            for include_param in include_params:
                                if include_param is '' or include_param in current_full_path:
                                    for exclude_param in exclude_params:
                                        if exclude_param is '':
                                            if not current_full_path in test_list:
                                                test_list.append(current_full_path)
                                        else:
                                            if exclude_param not in current_full_path:
                                                if not current_full_path in test_list:
                                                    test_list.append(current_full_path)
        if len(test_list) == 0:
            logger.error('\'%s\' does not contain tests based on your search criteria. Exiting program.' % tests_dir)
        else:
            logger.debug('List of all tests found: [%s]' % ', '.join(map(str, test_list)))

    return test_list


def path_warning(path):
    logger.error('Path not found: %s' % path)
    logger.critical('This can happen when Iris can\'t find your code root.')
    logger.critical('Try setting these environment variables:')
    if OSHelper.is_windows():
        logger.critical('\tsetx IRIS_CODE_ROOT %CD%')
        logger.critical('\tsetx PYTHONPATH %CD%')
        logger.critical('\nYou must restart your terminal for this to take effect.\n')
    else:
        logger.critical('\texport IRIS_CODE_ROOT=$PWD')
        logger.critical('\texport PYTHONPATH=$PWD')

