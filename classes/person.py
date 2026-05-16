class Person:
    """
    Represents a person, holds name, client socket and IP address
    """
    def __init__(self,addr,client_socket):
        self.addr = addr
        self.client_socket = client_socket
        self.name = None

    def set_name(self, name):
        """
        Sets the person's name
        :param name: str
        :return: None
        """
        self.name=name

    def __repr__(self):
        return f"Person({self.addr},{self.name})"
