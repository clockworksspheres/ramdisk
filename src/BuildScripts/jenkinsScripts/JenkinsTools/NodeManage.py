

class NodeManage():
    def __init__(self, args):
        self.args = args
        print(f"Initializing {self.__class__.__name__} class")

        try:
            self.server = jenkins.Jenkins(
                self.args.url,
                username=self.args.user,
                password=self.args.token
            )

            print("Instantiated server...")

            # Quick connectivity check
            try:
                self.server.get_whoami()
            except Exception as e:
                print("\nCannot connect to Jenkins!", file=sys.stderr)
                print("Common causes:", file=sys.stderr)
                print("  • Wrong --url")
                print("  • Jenkins not running / wrong port")
                print("  • Firewall / network issue")
                print("  • Invalid --user or --token")
                print(f"\nError detail: {e}", file=sys.stderr)
                sys.exit(1)

        except JenkinsException as e:
            print(f"\nJenkins API error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"\nUnexpected error: {e}", file=sys.stderr)
            sys.exit(1)

    def delete_node(self):
        """
        """
        self.server.delete_node(self.args.name)

    def disable_node(self):
        """
        """
        self.server.disable_node(self.args.name)

    def enable_node(self):
        """
        """
        self.server.enable_node(self.args.name)

    def add_node(self):
        """
        """
        from AddJenkinsNode import AddJenkinsNode
        jnode = AddJenkinsNode(self.args)
        jnode.add_jenkins_node()

    def update_node(self):
        """
        """
        from update_node import cmd_update_node()
        cmd_update_node(self.args)

        


