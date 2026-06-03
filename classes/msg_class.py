
class Message:
    """ Message class , includes the name(who sent), the text of the message, the time of the message
    ,and who needs to get the message"""
    def __init__(self, msg_date, name, info, to, data=None, file_type=""):
        self.msg_date = msg_date
        self.name = name
        self.info = info
        self.to = to
        self.data = data
        self.file_type = file_type
        self.scan_report = ""


    def get_date(self):
        return self.msg_date

    def get_name(self):
        return self.name

    def get_info(self):
        return self.info

    def get_to(self):
        return self.to

 
    def __repr__(self):
        return"{}\nFrom {}\n{}\n\nTo: {}\n\n".format(self.msg_date, self.name, self.info, self.to)



