import sys
import jenkins
from jenkins import JenkinsException

class NodeStatus():

    def __init__(self, args):
        self.args = args
        print(f"Initializing {self.__class__.__name__} class")

        try:
            self.server = jenkins.Jenkins(self.args.url, username=self.args.user, password=self.args.token)

            print("Instanciated server...")

            # Quick connectivity check
            try:
                server.get_whoami()
            except Exception as e:
                print("\nCannot connect to Jenkins!", file=sys.stderr)
                print("Common causes:", file=sys.stderr)
                print("  • Wrong --url (must be real address – not jenkins.example.com)", file=sys.stderr)
                print("  • Jenkins not running / wrong port", file=sys.stderr)
                print("  • Firewall / network issue", file=sys.stderr)
                print("  • Invalid --user or --token", file=sys.stderr)
                print(f"\nError detail: {e}", file=sys.stderr)
                sys.exit(1)

        except JenkinsException as e:
            print(f"\nJenkins API error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"\nUnexpected error: {e}", file=sys.stderr)
            sys.exit(1)

    def assert_node_exists(self):
        """
        """
        self.server.assert_node_exists(name, exception_message="node[%s] does not exist")

    def node_exists(self):
        """
        """
        exists = False
        exists = self.server.node_exists(name)
        return exists

    def get_nodes(self):
        """
        """
        return self.server.get_nodes()

    def get_node_info(self):
        """
        """
        return self.server.get_node_info(self.args.name)

    def get_node_config(self):
        """
        """
        return self.server.get_node_config(self.args.name)

