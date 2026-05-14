from imapclient import IMAPClient
import email
import os

class IMAPManager:
    def __init__(self, server, port, username, password, use_ssl=True):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.client = None

    def connect(self):
        self.client = IMAPClient(self.server, port=self.port, ssl=self.use_ssl)
        self.client.login(self.username, self.password)

    def disconnect(self):
        if self.client:
            self.client.logout()
            self.client = None

    def get_quota(self):
        """Returns quota information if supported by the server."""
        try:
            # IMAP QUOTA is an extension, not all servers support it
            quota = self.client.get_quota("INBOX")
            # quota is usually a list of quotas, each being a tuple (resource, usage, limit)
            return quota
        except Exception as e:
            print(f"Quota not supported or error: {e}")
            return None

    def fetch_messages_ids(self, folder='INBOX', criteria='ALL'):
        self.client.select_folder(folder)
        return self.client.search(criteria)

    def download_message(self, msg_id):
        res = self.client.fetch([msg_id], ['RFC822'])
        return res[msg_id][b'RFC822']

    def restore_message(self, eml_content, folder='INBOX'):
        """Restores a message to the server using IMAP APPEND."""
        # eml_content should be bytes
        self.client.append(folder, eml_content)

    def delete_messages(self, msg_ids):
        self.client.delete_messages(msg_ids)
        self.client.expunge()

if __name__ == "__main__":
    # Example usage (not intended to run without real credentials)
    print("IMAPManager loaded.")
