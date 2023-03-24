import os
from pathlib import Path
from typing import Set

from sretoolbox.utils.logger import get_text_logger

from managedtenants.utils.general_utils import run
from managedtenants.utils.types import AddonsByType


class ChangeDetector:
    def __init__(self, addons_dir, dry_run=True):
        self.dry_run = dry_run
        self.addons_dir = addons_dir
        self.log = get_text_logger("app")

    def get_changed_addons_by_type(self) -> AddonsByType:
        """
        Get the list of all changed addons.
        """
        addons_dir = Path(self.addons_dir).resolve()
        all_addons = set(addons_dir.iterdir())
        changed_files = self._get_changed_files()
        return self.find_types_of_changed_bundles(addons=all_addons,
                                                  changed_files=changed_files)

    @staticmethod
    def find_types_of_changed_bundles(addons: Set[Path], changed_files: Set[Path]) -> AddonsByType:
        """
        Abstraction to find all parents that have at least one child path listed
        in children.

        :param addons: set of parent directories
        :param changed_files: set of child paths
        """
        package_res = set()
        olm_res = set()
        for file in changed_files:
            addon_match = set(file.parents).intersection(addons)
            if len(addon_match) == 0:
                continue

            package_bundle_dir = list(addon_match)[0] / "package"
            if package_bundle_dir in file.parents:
                package_res.update(addon_match)
            else:
                olm_res.update(addon_match)

        return AddonsByType(olm_res, package_res)

    def _get_changed_files(self):
        """
        Detect changed files within managed-tenants and managed-tenants-bundles.

        Remote name has to be origin and principal branch called main, which is
        the case for both repositories.
        """
        if self.dry_run:
            # pr_check
            commit_range = "remotes/origin/main...HEAD"
        else:
            # build_deploy
            # From https://plugins.jenkins.io/git/
            git_previous_commit = os.environ["GIT_PREVIOUS_COMMIT"]
            git_commit = os.environ["GIT_COMMIT"]
            commit_range = f"{git_previous_commit}...{git_commit}"

        changed_files = set()
        cmd = [
            "git",
            "diff",
            "--name-only",
            f"{commit_range}",
        ]
        result = run(cmd, self.log).stdout.decode().strip()
        for diff in result.splitlines():
            changed_files.add(Path(diff).resolve())
        return changed_files


def get_short_hash(size=7):
    """
    TODO
    :param size:
    :return:
    """
    cmd = ["git", "rev-parse", f"--short={size}", "HEAD"]
    return run(cmd=cmd).stdout.decode().strip()
