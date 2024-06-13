import streamlit as st
import logging
import boto3
from botocore.exceptions import ClientError
import json
import os

#BEDROCK PART
# Fetch AWS credentials from environment variables
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION', 'us-west-2')

class BedrockWrapper:
  
    def __init__(self, service, region):
        """ Initiates the bedrock client and runtime """
        self.bedrock_client = boto3.client(service_name=service, region_name=region)
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)

    def list_foundation_models(self):
        """ List the foundational models available """
        response = self.bedrock_client.list_foundation_models()
        models = response["modelSummaries"]
        print(f"Got {len(models)} foundation models.", models)

    def set_model(self, model_id):
        """ Sets the generative AI model ID to be used """
        self.model_id = model_id

    def generate_body(self, prompt, params):
        """ Sets model parameters and prompt """
        body = json.dumps({
            'prompt': prompt,
            **params
        })
        return body

    def invoke_model(self, body):
        """ Calls the model and gets response string """
        accept = 'application/json'
        contentType = 'application/json'
        response = self.bedrock_runtime.invoke_model(
            body=body, modelId=self.model_id, 
            accept=accept, contentType=contentType
        )
        response_body = json.loads(response['body'].read())
        result = response_body.get('completion')
        return result

# Initialize Bedrock
bedrock = BedrockWrapper("bedrock", AWS_REGION)
model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
bedrock.set_model(model_id)

params = {
    "max_tokens_to_sample": 1000,
    "temperature": 0.1,
    "top_p": 0.1,
}

# STREAMLIT
# Store the initial value of widgets in session state
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False

col1, col2 = st.columns(2)

with col1:
    st.checkbox("Disable selectbox widget", key="disabled")
    st.radio(
        "Set selectbox label visibility 👉",
        key="visibility",
        options=["visible", "hidden", "collapsed"],
    )

with col2:
    project_status = st.selectbox(
        "What is your project status?",
        ("Green 🟢", "Yellow 🟡", "Red 🔴"),
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
    )

#Green Status summary
if project_status == "Green 🟢":
    st.write("This seems to be on the right track! Good job!")
    project_name = st.text_input('Enter the project name:')
    executive_summary = st.text_area('Executive Summary:')
    project_target_date = st.date_input("Target Project Completion Date:")
    project_status_this_week = st.selectbox(
        "What is the status of your project this week?",
        ("On Track", "At Risk", "Off Track"),
    )
    project_activities_this_week = st.text_area('Project Activities this week:')
    project_activities_next_week = st.text_area('Project Activities for next week:')
    
    #Generate summary for Green Status
    if st.button('Generate Summary'):
        if project_name and executive_summary and project_activities_this_week and project_activities_next_week:
            prompt = f"""Human: You are an Engagement manager expert and you have to generate a project status each week based on the project colour. 
                If the project status from {project_status} is green you have to generate the summary of the project using this example: 
                Green Status Example 
                Project Status: Green 
                Project Status Notes:
                EXECUTIVE SUMMARY: The project is on track with no major risks or issues identified.
                WEEKLY UPDATE: Mobilize project is on schedule to migrate X apps by {{date}}; five of the eight work streams are active. No major risks identified. Budget and timing are on track.
        Here are the information collected <transcript>{project_name}, {executive_summary}, {project_activities_this_week}, {project_activities_next_week}, {project_target_date} </transcript> let's go
        Assistant:"""

            body = bedrock.generate_body(prompt, params)
            summary = bedrock.invoke_model(body)
            st.write("Summary:", summary)
        else:
            st.error("Please fill in all the fields to generate the summary.")


if project_status == "Yellow 🟡":
    st.write("Don't worry it will be fine")
    project_name = st.text_input('Enter the project name:')
    executive_summary = st.text_area('Executive Summary:')
    project_target_date = st.date_input("Target Project Completion Date:")
    project_status_this_week = st.selectbox(
        "What is the status of your project this week?",
        ("On Track", "At Risk", "Off Track"),
    )
    project_activities_this_week = st.text_area('Project Activities this week:')
    project_activities_next_week = st.text_area('Project Activities for next week:')
    project_primary_yellow_reason = st.selectbox (
        "What is the primary reason for a Yellow status? : if any doubt please refer to the wiki page : https://w.amazon.com/bin/view/AWS/Teams/Proserve/Delivery/StatusReporting/ ",
        ("Pre-SOW - Work at risk (WAR)","Scope - ProServe Initiated,Custom solution gap","Customer - Market/business factors","ProServe – Delivery delay","ProServe - Service/ Platform/ Product","ProServe – Budget","ProServe – Consultant Availability/Skill Gap","ProServe - Delivery Quality","ProServe - Work at Risk (WAR)","Customer - Budget Reduction","Customer – Delay/Hold","Customer – Alignment","Customer - Readiness","Customer – Resource Availability/Capacity/Skill Gap","Customer - Required Onboarding/Screening of ProServe Consultants","Customer - Sponsor","Partner – Delivery delay","Partner - Delivery Quality","Partner - Alignment","Partner – Resource Availability/Skill Gap","Contract","Scope - Customer","Security","Third party dependency (ISV, Vendor, SI, Regulator)"),
    )
    project_open_ehi_flags = st.text_area ('Open EHI Flags:')
    project_margin = st.text_area ('Project Margin:')
    project_risk = st.text_area ('Project Risk:')
    if st.button('Generate Summary'):
        if project_name and executive_summary and project_activities_this_week and project_activities_next_week:
            prompt = f"""Human: You are an Engagement manager expert and you have to generate a project status each week based on the project colour. You will use the human input and the expert project management practices to elaborate a get to green path based on the {project_risk} stated
                
                
                If the project status from {project_status} is yellow, you have to generate the summary of the project using this example: 
                Yellow Status Example
                
                Project Status: Yellow
                
                Primary Yellow Status Reason: Scope - Change Request/Creep/Undefined
                
                Project Status Notes:

                [EXECUTIVE SUMMARY]
                Customer ABC is migrating its cashless payment and processing platform from Oracle (OCI) to AWS. The platform comprises 100 applications, 500 servers, and 700TB of PostgreSQL databases. This migration allows ABC to meet its business target of closing 2 data centers by December 15, 2023. The data center exit will reduce ABC’s data center expenses by $2M annually. This 16-week Mobilize engagement spans 6 work streams. They are: Landing Zone/Control Tower, Operations, Security, People & Change, Portfolio, and Migration.

                Open EHI Flags: DSR - review with engagement security slated for April 3, 2023. DSR close out date is April 7, 2023.

                Project Margin: ABC has a Project Margin variance of -5 percentage points (50% as sold vs. 45% as delivered). This variance is driven by two roles sold as L5 roles but staffed with L6 consultants. L6 consultants were needed to deliver the customer business outcome.

                SITUATION: ABC is yellow trending yellow. Schedule is at risk due to ABC experiencing attrition in key roles such as PostgreSQL developers, and database administrators. Continued attrition can impact PostgreSQL code conversion work supporting Oracle Exadata to PostgreSQL modernization and overall migration. Status across the 6 work streams is as follows:

                Landing Zone/Control Tower: The sprint goal is to deploy DNS in the Dev environment and the key deliverable this sprint is the completed deployment of DNS in Dev by April 4, 2023. The goal next sprint is to complete the DNS documentation in Confluence.
                Operations: The sprint goal is to define the disaster recovery strategy for ABC. The key deliverable is the documentation of the DR strategy in Confluence by April 4, 2023. The focus for next sprint is the implementation of the DR strategy
                Security: The sprint goal is to create a Runbook for Break Glass and the deliverable is a completed Runbook on confluence by April 4, 2023. The focus for next sprint is to complete the design for incident response.
                People & Change: The sprint goal is to draft the Cloud Center of Excellence (CCOE) charter. The key deliverable is the first draft of the CCOE charter by April 4, 2023. Next sprint’s goal is to complete the CCOE charter and present for ABC sign off.
                Portfolio: The goal this sprint is to validate migration list dependencies. The key deliverable is the updated migration plan with dependencies and owners identified by April 4, 2023. Next sprint will focus on finalizing the overall migration plan.
                Migration: The sprint goal is to resolve errors reported in PostgreSQL import scripts by April 4, 2023. The goal next sprint is to kick off data migration for the Dev environment.
                IMPACT: If ABC loses one more developer or database administrator, the code conversion work with fall behind by 2 weeks translating to an overall migration schedule delay of 1 month. This will jeopardize ABC’s data center exit timeline.

                GET-TO-GREEN PLAN:
                Monitor ABC staff attrition trends and discuss how ProServe/partner can assist with staffing needs for ABC

                Owner: EM
                Status: In progress
                Target completion date: 06-04-2023
                DSR Completion
                Owner: EM
                Status: In progress
                Target Completion Date: 07-04-2023
                Key Risks/Issues:

                Risk (R-001 - open]: Tight migration timeline with little slack in the schedule for delays
                Mitigation: Continue to inspect sprints across migration program and remediate risks/issues that impact schedule.
                Owner: IJK (EM)
                Target Close Date: 15-03-2024
                Issue (I-002 - open): ABC Staff Attrition
                Mitigation: Work with ABC to monitor attrition trends. Status for immediate attention. Recommend options for ProServe to help mitigate issues by providing staff to support.
                Owner: IJK (EM)
                Target Close Date:15-09-2023
                [OWNERS]: EFG (EM)
                [TARGET RESOLUTION DATE]: 07-04-2023
                TARGET PROJECT COMPLETION DATE: 15-12-2023

                CUSTOMER TEMPERATURE: yellow - the customer is concerned about attrition and unplanned schedule delays. The customer returned a CFF rating of “very satisfied” on March 1, 2023.

                Here are links to the Risk Log and Issue Log
        Here are the information collected <transcript>{project_name}, {executive_summary}, {project_primary_yellow_reason}, {project_target_date}, {project_status_this_week}, {project_activities_this_week}, {project_activities_next_week}, {project_risk}, {project_open_ehi_flags}, {project_margin}  </transcript> let's go
        Assistant:"""

            body = bedrock.generate_body(prompt, params)
            summary = bedrock.invoke_model(body)
            st.write("Summary:", summary)
        else:
            st.error("Please fill in all the fields to generate the summary.")

if project_status == "Red 🔴":
    st.write("Don't worry it will be fine")
    project_name = st.text_input('Enter the project name:')
    executive_summary = st.text_area('Executive Summary:')
    project_target_date = st.date_input("Target Project Completion Date:")
    project_status_this_week = st.selectbox(
        "What is the status of your project this week?",
        ("On Track", "At Risk", "Off Track"),
    )
    project_activities_this_week = st.text_area('Project Activities this week:')
    project_activities_next_week = st.text_area('Project Activities for next week:')
    project_primary_red_reason = st.selectbox (
        "What is the primary reason for a Yellow status? : if any doubt please refer to the wiki page : https://w.amazon.com/bin/view/AWS/Teams/Proserve/Delivery/StatusReporting/ ",
        ("Pre-SOW - Work at risk (WAR)","Scope - ProServe Initiated,Custom solution gap","Customer - Market/business factors","ProServe – Delivery delay","ProServe - Service/ Platform/ Product","ProServe – Budget","ProServe – Consultant Availability/Skill Gap","ProServe - Delivery Quality","ProServe - Work at Risk (WAR)","Customer - Budget Reduction","Customer – Delay/Hold","Customer – Alignment","Customer - Readiness","Customer – Resource Availability/Capacity/Skill Gap","Customer - Required Onboarding/Screening of ProServe Consultants","Customer - Sponsor","Partner – Delivery delay","Partner - Delivery Quality","Partner - Alignment","Partner – Resource Availability/Skill Gap","Contract","Scope - Customer","Security","Third party dependency (ISV, Vendor, SI, Regulator)"),
    )
    project_open_ehi_flags = st.text_area ('Open EHI Flags:')
    project_margin = st.text_area ('Project Margin:')
    project_risk = st.text_area ('Project Risk:')
    if st.button('Generate Summary'):
        if project_name and executive_summary and project_activities_this_week and project_activities_next_week:
            prompt = f"""Human: You are an Engagement manager expert and you have to generate a project status each week based on the project colour. You will use the human input and the expert project management practices to elaborate a get to green path based on the {project_risk} stated
                
                
                If the project status from {project_status} is red, you have to generate the summary of the project using this example: 
                Red Status Example
                
                Project Status: Red
                
                Primary Red Status Reason: Scope - Change Request/Creep/Undefined
                

                Project Status Notes:

                [EXECUTIVE SUMMARY]
                Customer ABC is migrating its cashless payment and processing platform from Oracle (OCI) to AWS. The platform comprises 100 applications, 500 servers, and 700TB of PostgreSQL databases. This migration allows ABC to meet its business target of closing 2 data centers by December 15, 2023. The data center exit will reduce ABC’s data center expenses by $2M annually. This 16-week Mobilize engagement spans 6 work streams. They are: Landing Zone/Control Tower, Operations, Security, People & Change, Portfolio, and Migration.

                Open EHI Flags: DSR - review with engagement security slated for April 3, 2023. DSR close out date is April 7, 2023.

                Project Margin: ABC has a Project Margin variance of -5 percentage points (50% as sold vs. 45% as delivered). This variance is driven by two roles sold as L5 roles but staffed with L6 consultants. L6 consultants were needed to deliver the customer business outcome.

                SITUATION: ABC is red trending yellow. Schedule is at risk due to ABC experiencing attrition in key roles such as PostgreSQL developers, and database administrators. Continued attrition can impact PostgreSQL code conversion work supporting Oracle Exadata to PostgreSQL modernization and overall migration. Status across the 6 work streams is as follows:

                Landing Zone/Control Tower: The sprint goal is to deploy DNS in the Dev environment and the key deliverable this sprint is the completed deployment of DNS in Dev by April 4, 2023. The goal next sprint is to complete the DNS documentation in Confluence.
                Operations: The sprint goal is to define the disaster recovery strategy for ABC. The key deliverable is the documentation of the DR strategy in Confluence by April 4, 2023. The focus for next sprint is the implementation of the DR strategy
                Security: The sprint goal is to create a Runbook for Break Glass and the deliverable is a completed Runbook on confluence by April 4, 2023. The focus for next sprint is to complete the design for incident response.
                People & Change: The sprint goal is to draft the Cloud Center of Excellence (CCOE) charter. The key deliverable is the first draft of the CCOE charter by April 4, 2023. Next sprint’s goal is to complete the CCOE charter and present for ABC sign off.
                Portfolio: The goal this sprint is to validate migration list dependencies. The key deliverable is the updated migration plan with dependencies and owners identified by April 4, 2023. Next sprint will focus on finalizing the overall migration plan.
                Migration: The sprint goal is to resolve errors reported in PostgreSQL import scripts by April 4, 2023. The goal next sprint is to kick off data migration for the Dev environment.
                IMPACT: If ABC loses one more developer or database administrator, the code conversion work with fall behind by 2 weeks translating to an overall migration schedule delay of 1 month. This will jeopardize ABC’s data center exit timeline.

                GET-TO-GREEN PLAN:
                Monitor ABC staff attrition trends and discuss how ProServe/partner can assist with staffing needs for ABC

                Owner: EM
                Status: In progress
                Target completion date: 06-04-2023
                DSR Completion
                Owner: EM
                Status: In progress
                Target Completion Date: 07-04-2023
                Key Risks/Issues:

                Risk (R-001 - open]: Tight migration timeline with little slack in the schedule for delays
                Mitigation: Continue to inspect sprints across migration program and remediate risks/issues that impact schedule.
                Owner: IJK (EM)
                Target Close Date: 15-03-2024
                Issue (I-002 - open): ABC Staff Attrition
                Mitigation: Work with ABC to monitor attrition trends. Status for immediate attention. Recommend options for ProServe to help mitigate issues by providing staff to support.
                Owner: IJK (EM)
                Target Close Date:15-09-2023
                [OWNERS]: EFG (EM)
                [TARGET RESOLUTION DATE]: 07-04-2023
                TARGET PROJECT COMPLETION DATE: 15-12-2023

                CUSTOMER TEMPERATURE: yellow - the customer is concerned about attrition and unplanned schedule delays. The customer returned a CFF rating of “very satisfied” on March 1, 2023.

                Here are links to the Risk Log and Issue Log
        Here are the information collected <transcript>{project_name}, {executive_summary}, {project_primary_red_reason}, {project_target_date}, {project_status_this_week}, {project_activities_this_week}, {project_activities_next_week}, {project_risk}, {project_open_ehi_flags}, {project_margin}  </transcript> let's go
        Assistant:"""

            body = bedrock.generate_body(prompt, params)
            summary = bedrock.invoke_model(body)
            st.write("Summary:", summary)
        else:
            st.error("Please fill in all the fields to generate the summary.")
