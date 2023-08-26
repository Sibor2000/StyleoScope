import os
import streamlit as st
import pandas as pd
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
from dotenv import load_dotenv

from colors import ColorResult

load_dotenv()

USER_ID = 'pizzahunter2000'
# Your PAT (Personal Access Token) can be found in the portal under Authentification
PAT = os.getenv("CLARIFAI_TOKEN")
APP_ID = 'ReFashion001'
# Change these to make your own predictions
WORKFLOW_ID = 'workflow-c4a9f1'
IMAGE_URL = 'https://samples.clarifai.com/metro-north.jpg'

channel = ClarifaiChannel.get_grpc_channel()
stub = service_pb2_grpc.V2Stub(channel)
metadata = (('authorization', 'Key ' + PAT),)
userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

def runWorkflow(file):
    post_workflow_results_response = stub.PostWorkflowResults(
        service_pb2.PostWorkflowResultsRequest(
            user_app_id=userDataObject,  
            workflow_id=WORKFLOW_ID,
            inputs=[
                resources_pb2.Input(
                    data=resources_pb2.Data(
                        image=resources_pb2.Image(
                            base64=file
                        )
                    )
                )
            ]
        ),
        metadata=metadata
    )
    if post_workflow_results_response.status.code != status_code_pb2.SUCCESS:
        print(post_workflow_results_response.status)
        raise Exception("Post workflow results failed, status: " + post_workflow_results_response.status.description)

    results = post_workflow_results_response.results[0]
    return results

# Converts the results from the Clarifai Workflow to a list of ColorResult objects
def getColors(results):
    colorResults = []
    for output in results.outputs:
        if output.model.id == "color-recognition":
            for color in output.data.colors:
                colorResults.append(ColorResult(color.raw_hex, color.w3c, color.value))
    return colorResults

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    results = runWorkflow(uploaded_file.read())
    colors = getColors(results)
    # Create a table of name and hex values
    st.write(pd.DataFrame.from_records([{ 'name': color.name, 'hex': color.hex } for color in colors]))