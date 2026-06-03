class Person:
    """
    Represents a person, holds name, client socket and IP address
    """
    def __init__(self,addr,client_socket):
        self.addr = addr
        self.client_socket = client_socket
        self.mail = None
        self.waiting_msgs = []

    def set_mail(self, mail):
        """
        Sets the person's name
        :param name: str
        :return: None
        """
        self.mail=mail

    def __repr__(self):
        return f"Person({self.addr},{self.mail})"
