from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.exceptions import OutputParserException
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import JsonOutputParser
import os

groq_api_key = ""














# models that can be used- deepseek-r1-distill-llama-70b  mixtral-8x7b-32768  llama-3.3-70b-versatile
class Chain:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=groq_api_key,
            model_name="mixtral-8x7b-32768"
        )

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills` and `description`.
            For the skills field, please return it as a string with skills separated by commas.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def write_mail(self, job, links):

        if links:
            formatted_links = "\n".join([f"{i + 1}. {link}" for i, link in enumerate(links, 1)])
        else:
            formatted_links = "No specific portfolio links available."

        email_prompt = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### PORTFOLIO LINKS:
            {link_list}

            ### INSTRUCTION:
            You are Mohan, a business development executive at AtliQ. AtliQ is an AI & Software Consulting company dedicated to facilitating
            the seamless integration of business processes through automated tools. 
            Over our experience, we have empowered numerous enterprises with tailored solutions, fostering scalability, 
            process optimization, cost reduction, and heightened overall efficiency. 

            Write a cold email to the client regarding the job mentioned above describing the capability of AtliQ in fulfilling their needs.
            When showcasing AtliQ's portfolio:
            1. Use the actual portfolio links provided above
            2. Mention the relevant technologies from the portfolio when referencing each link
            3. Make sure the links are properly integrated into the email context

            Remember you are Mohan, BDE at AtliQ. 
            Do not provide a preamble.

            ### EMAIL (NO PREAMBLE):
            """
        )

        email_extract = email_prompt | self.llm
        res = email_extract.invoke(input={
            "job_description": str(job),
            "link_list": formatted_links
        })
        return res.content

    @staticmethod
    def validate_api_key():
        """Validate if the API key is set and accessible"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        return api_key


if __name__ == "__main__":
    Chain.validate_api_key()