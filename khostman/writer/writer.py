import shutil
from pathlib import Path
from datetime import datetime
from khostman.formatter.formatter import Formatter
from khostman.utils.os_utils import OSUtils
from khostman.utils.logging_utils import LoggingUtils
from khostman.logger.logger import logger
from khostman.cli.prompt import UserInteraction
from khostman.unique_domains.unique_domains import UniqueDomains


class Writer:
    path = OSUtils().path_to_hosts()

    @staticmethod
    def header():
        return \
            f"""
# This Hosts file was generated using the Khostman app
#
# Updated: {datetime.now().strftime("%d-%b-%Y")}
#
# Total amount of entries:
#
# Github repository: https://github.com/kravchenkoda/khostman
#
#
#######################################
127.0.0.1 localhost
127.0.0.1 localhost.localdomain
127.0.0.1 local
255.255.255.255 broadcasthost
::1 localhost
::1 ip6-localhost
::1 ip6-loopback
fe80::1%lo0 localhost
ff00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
ff02::3 ip6-allhosts
"""

    def write_to_hosts(self) -> None:
        """
        Writes domains to the system's hosts file.
        """
        blacklist_domains = UniqueDomains().get_unique_domains()
        print(f'Writing to {self.path}...')
        with open(self.path, 'w') as hosts:
            for line in blacklist_domains:
                hosts.write(line)

        print(f'Blocked {len(blacklist_domains)} websites.')

    def block_domain(self, *args):
        with open(self.path, 'a+') as hosts:
            hosts.write("\n############   User's custom blocked hosts   ############\n\n")
            for website in args:
                hosts.write(f"0.0.0.0 {website}\n")
                logger.debug(f'Blacklisted {website}')

    @LoggingUtils.func_and_args_logging
    def whitelist_domain(self, whitelisted_url):
        """
        Removes the given domain name from the blacklisted domains in the system's Hosts file if it is present.

        Args:
            whitelisted_url (str): The domain to be whitelisted.
        Returns:
            None
        """
        temp_hosts_path = self.path.with_suffix('.temp')

        with open(temp_hosts_path, 'w') as temp:
            with open(self.path, 'r') as original:
                whitelisted_url = Formatter().strip_domain_prefix(whitelisted_url)
                found = False
                for line in original:
                    if whitelisted_url in line:
                        found = True
                        continue
                    temp.write(line)

                if not found:
                    print(f"No occurrence of '{whitelisted_url}'"
                          f" found in file '{self.path}'")
                    logger.info(f"No occurrence of '{whitelisted_url}'"
                                f" found in file '{self.path}'")
        self.path.unlink()
        temp_hosts_path.rename(self.path)

    @LoggingUtils.func_and_args_logging
    def create_backup(self):
        """Creates the backup of the user's original Hosts file"""
        backup_path = UserInteraction().ask_backup_directory()
        if not backup_path:
            return
        backup_hosts = Path(backup_path) / 'hosts_backup'
        try:
            with self.path.open('rb') as src, backup_hosts.open('wb') as dst:
                shutil.copyfileobj(src, dst)
            print(f'Backup file was created here: {backup_path}')
            logger.info('Backup of the original Hosts'
                        f' file was created at: {backup_path}')
        except OSError as e:
            logger.warning(f'Error creating backup: {e}')
            print(f'Error creating backup: {e}')
