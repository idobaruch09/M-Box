
class Message:
    """ Message class , includes the name(who sent), the text of the message, the time of the message
    , who needs to get the message, the file-data and it's type"""
    def __init__(self, msg_date, name, info, to, data=None, file_type=""):
        self.msg_date = msg_date
        self.name = name
        self.info = info
        self.to = to
        self.data = data
        self.file_type = file_type
        self.scan_report = "No report"


    def get_date(self):
        return self.msg_date

    def get_name(self):
        return self.name

    def get_info(self):
        return self.info

    def get_to(self):
        return self.to

 
    def __repr__(self):
        return f"{self.msg_date}\nFrom: {self.name}\n\nScan report: {self.scan_report}\n\n{self.info}\n\nTo: {self.to}\n"



