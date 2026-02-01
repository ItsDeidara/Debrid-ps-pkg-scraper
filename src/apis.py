import requests

class RealDebridAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.real-debrid.com/rest/1.0"

    def unrestrict_link(self, link):
        url = f"{self.base_url}/unrestrict/link"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {"link": link}
        response = requests.post(url, headers=headers, data=data)
        return response.json()