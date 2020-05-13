import paramiko


class connection:
    def __init__(self, host, name, password):
        self.host = host
        self.name = name
        self.password = password

    def connect(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.host, username=self.name, password=self.password)

        stdin, stdout, stderr = client.exec_command('cat /proc/net/arp')
        for line in stdout.readlines():
            print(line)

        client.close()


conn = connection('qzhub.hopto.org', 'QZhub', 'q8@XL4sqL9qaYQ2')

