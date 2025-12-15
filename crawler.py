import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import time

class Crawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.results = []
        
    def get_page_title(self, url):
        """Extract title from a webpage"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if soup.title:
                return soup.title.string.strip()
            return "No title found"
            
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return "Error fetching title"
    
    def crawl_topic(self, topic_name, queries, urls):
        """Process URLs for a specific topic"""
        print(f"\nProcessing: {topic_name}")
        
        topic_data = {
            "topic": topic_name,
            "queries": queries,
            "articles": []
        }
        
        for idx, url in enumerate(urls):
            print(f"  [{idx+1}/{len(urls)}] Fetching: {url}")
            
            title = self.get_page_title(url)
            
            prefix = topic_name.split('.')[0].strip()
            unique_id = f"article_{prefix}_{idx+1:03d}"
            
            article = {
                "unique_id": unique_id,
                "timestamp": datetime.utcnow().isoformat() + 'Z',
                "url": url,
                "title": title
            }
            
            topic_data["articles"].append(article)
            time.sleep(1) 
        
        return topic_data
    
    def save_results(self, filename="articles.json"):
        """Save to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\nSaved to {filename}")


def main():
    crawler = Crawler()
    
    topics = [
        {
            "name": "1. DDoS Attack",
            "queries": ["What is a DDoS attack?", "How does a DDoS attack work?"],
            "urls": [
                "https://www.cloudflare.com/learning/ddos/what-is-a-ddos-attack/",
                "https://www.kaspersky.com/resource-center/threats/ddos-attacks/",
                "https://www.fortinet.com/resources/cyberglossary/ddos-attack",
                "https://www.cisco.com/c/en/us/products/security/ddos-defense/what-is-ddos-attack.html",
                "https://www.imperva.com/learn/ddos/ddos-attacks/"
            ]
        },
        {
            "name": "2. Phishing",
            "queries": ["What is phishing in cybersecurity?", "How can I protect myself from phishing emails?"],
            "urls": [
                "https://www.ibm.com/think/topics/phishing",
                "https://www.cisco.com/c/en/us/products/security/email-security/what-is-phishing.html",
                "https://www.proofpoint.com/us/threat-reference/phishing",
                "https://www.ftc.gov/business-guidance/resources/phishing",
                "https://www.cisa.gov/secure-our-world/recognize-and-report-phishing"
            ]
        },
        {
            "name": "3. SQL Injection",
            "queries": ["What is SQL injection?", "How do attackers perform SQL injection?"],
            "urls": [
                "https://www.cloudflare.com/learning/security/threats/sql-injection/",
                "https://portswigger.net/web-security/sql-injection",
                "https://owasp.org/www-community/attacks/SQL_Injection",
                "https://www.acunetix.com/websitesecurity/sql-injection/",
                "https://www.imperva.com/learn/application-security/sql-injection-sqli/"
            ]
        },
        {
            "name": "4. Malware",
            "queries": ["What is malware?", "What are the common types of malware?"],
            "urls": [
                "https://www.malwarebytes.com/malware",
                "https://www.kaspersky.com/resource-center/threats/malware",
                "https://www.crowdstrike.com/cybersecurity-101/malware/",
                "https://www.cisco.com/c/en/us/products/security/advanced-malware-protection/what-is-malware.html",
                "https://www.microsoft.com/en-us/security/business/security-101/what-is-malware"
            ]
        },
        {
            "name": "5. Firewall",
            "queries": ["What is a firewall?", "How does a firewall protect a network?"],
            "urls": [
                "https://www.fortinet.com/resources/cyberglossary/firewall",
                "https://www.cisco.com/c/en/us/products/security/firewalls/what-is-a-firewall.html",
                "https://www.paloaltonetworks.com/cyberpedia/what-is-a-firewall",
                "https://www.checkpoint.com/cyber-hub/network-security/what-is-firewall/",
                "https://www.cloudflare.com/learning/security/what-is-a-firewall/"
            ]
        },
        {
            "name": "6. Encryption",
            "queries": ["What is encryption?", "Why is encryption important in cybersecurity?"],
            "urls": [
                "https://www.cloudflare.com/learning/ssl/what-is-encryption/",
                "https://www.kaspersky.com/resource-center/definitions/encryption",
                "https://cloud.google.com/learn/what-is-encryption",
                "https://www.ibm.com/think/topics/encryption",
                "https://www.cisco.com/c/en/us/products/security/encryption-explained.html"
            ]
        },
        {
            "name": "7. Two-Factor Authentication (2FA)",
            "queries": ["What is two-factor authentication?", "Why should I use 2FA?"],
            "urls": [
                "https://authy.com/what-is-2fa/",
                "https://www.cisa.gov/secure-our-world/turn-mfa",
                "https://www.microsoft.com/en-us/security/business/security-101/what-is-two-factor-authentication-2fa",
                "https://www.onelogin.com/learn/what-is-mfa",
                "https://auth0.com/intro-to-iam/what-is-two-factor-authentication-2fa"
            ]
        },
        {
            "name": "8. Cloud Security",
            "queries": ["What is cloud security?", "How can cloud services be protected from attacks?"],
            "urls": [
                "https://www.ibm.com/think/topics/cloud-security",
                "https://www.microsoft.com/en-us/security/business/security-101/what-is-cloud-security",
                "https://cloud.google.com/learn/what-is-cloud-security",
                "https://www.cisco.com/c/en/us/products/security/what-is-cloud-security.html",
                "https://www.crowdstrike.com/cybersecurity-101/cloud-security/"
            ]
        },
        {
            "name": "9. IoT Security",
            "queries": ["What is IoT security?", "How can IoT devices be secured?"],
            "urls": [
                "https://www.kaspersky.com/resource-center/definitions/what-is-iot-security",
                "https://www.fortinet.com/resources/cyberglossary/iot-security",
                "https://www.paloaltonetworks.com/cyberpedia/what-is-iot-security",
                "https://www.cisco.com/c/en/us/solutions/internet-of-things/iot-security.html",
                "https://www.cloudflare.com/learning/security/what-is-iot-security/"
            ]
        },
        {
            "name": "10. Cybersecurity Basics",
            "queries": ["What is cybersecurity?", "What are the common threats in cybersecurity?"],
            "urls": [
                "https://www.cisco.com/c/en/us/products/security/what-is-cybersecurity.html",
                "https://www.cisa.gov/cybersecurity",
                "https://www.fortinet.com/resources/cyberglossary/cybersecurity",
                "https://www.ibm.com/think/topics/cybersecurity",
                "https://www.microsoft.com/en-us/security/business/security-101/what-is-cybersecurity"
            ]
        }
    ]
    
    for topic in topics:
        topic_data = crawler.crawl_topic(
            topic['name'],
            topic['queries'],
            topic['urls']
        )
        crawler.results.append(topic_data)
    
    crawler.save_results()
    print("\nDone! Crawled all topics.")


if __name__ == "__main__":
    main()