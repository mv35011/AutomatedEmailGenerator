import time

import pandas as pd
import chromadb
import uuid
from typing import List
import re


class Portfolio:
    def __init__(self, file_path='C:/Users/mv350/Downloads/Documents/Pycharm_projects/AutomatedEmailGenerator/login_server/members/my_portfolio.csv'):
        self.file_path = file_path
        self.df = pd.read_csv(self.file_path)
        self.chroma_client = chromadb.PersistentClient('vectorstore')
        # Add timestamp to make collection name unique
        self.collection_name = f"portfolio_{int(time.time())}"
        self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name)
        self.load_portfolio()

    def load_portfolio(self):

        try:
            self.collection.delete(self.collection.get()["ids"])
        except:
            pass


        for _, row in self.df.iterrows():

            techstack = row["Techstack"].strip('"').lower()
            link = row["Links"].strip('"')

            self.collection.add(
                documents=[techstack],
                metadatas=[{"link": link, "techstack": techstack}],
                ids=[str(uuid.uuid4())]
            )

    def preprocess_skills(self, skills: str) -> str:
        """Preprocess skills string to improve matching"""
        # Handle case where skills might be a list
        if isinstance(skills, list):
            skills = ' '.join(skills)

        skills = str(skills).lower()  # Ensure skills is a string
        skill_list = [s.strip() for s in re.split(r'[,\s]+', skills)]
        skill_list = list(set(skill_list))
        return " ".join(skill_list)

    def query_link(self, skills: str) -> List[dict]:
        """Query links based on skills and return formatted results"""
        if not skills:
            return []


        processed_skills = self.preprocess_skills(skills)


        results = self.collection.query(
            query_texts=[processed_skills],
            n_results=3
        )

        links = []
        if results and 'metadatas' in results and results['metadatas']:
            for metadata in results['metadatas'][0]:
                if 'link' in metadata and 'techstack' in metadata:
                    links.append({
                        'link': metadata['link'],
                        'techstack': metadata['techstack']
                    })


        formatted_links = []
        for idx, item in enumerate(links, 1):
            tech_list = item['techstack'].split(',')
            tech_summary = ', '.join(tech_list[:2]) + ('...' if len(tech_list) > 2 else '')
            formatted_links.append(f"{item['link']} (Technologies: {tech_summary})")

        return formatted_links

    def get_all_links(self) -> List[dict]:
        """Get all portfolio links"""
        try:
            results = self.collection.get()
            links = []
            for metadata in results['metadatas']:
                if 'link' in metadata and 'techstack' in metadata:
                    links.append({
                        'link': metadata['link'],
                        'techstack': metadata['techstack']
                    })
            return links
        except Exception as e:
            print(f"Error retrieving links: {e}")
            return []