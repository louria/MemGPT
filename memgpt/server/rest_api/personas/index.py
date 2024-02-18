import uuid
import os
import json
from typing import List
from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel, Field
from functools import partial

from memgpt.server.server import SyncServer
from memgpt.server.rest_api.interface import QueuingInterface
from memgpt.server.rest_api.auth_token import get_current_user

router = APIRouter()


class ListPersonasResponse(BaseModel):
    personas: List[dict] = Field(..., description="List of persona configurations.")


def read_persona_file(file_path):
    with open(file_path, 'r') as f:
        name = os.path.splitext(os.path.basename(file_path))[0]  # get filename without extension
        text = f.read()
        return {'name': name, 'text': text}
    
def setup_personas_index_router(server: SyncServer, interface: QueuingInterface):
    get_current_user_with_server = partial(get_current_user, server)

    @router.get("/personas", tags=["personas"], response_model=ListPersonasResponse)
    async def list_personas(
        user_id: uuid.UUID = Depends(get_current_user_with_server),
    ):
        # Clear the interface
        interface.clear()

        # Get list of persona files
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        persona_folder = '../../../personas/examples'  # replace with actual path
        print(f'Persona folder: {persona_folder}')  # print persona_folder

        persona_files = [f for f in os.listdir(persona_folder) if os.path.isfile(os.path.join(persona_folder, f))]
        print(f'Persona files: {persona_files}')  # print persona_files

        # Read persona files and add to personas_data
        personas_data = [read_persona_file(os.path.join(persona_folder, f)) for f in persona_files]

        # TODO: Replace with actual data fetching logic once available
 #       personas_data = [
 #          {"name": "Persona 1", "text": "Details about Persona 1"},
 #           {"name": "Persona 2", "text": "Details about Persona 2"},
 #           {"name": "Persona 3", "text": "Details about Persona 3"},
 #       ]

        return ListPersonasResponse(personas=personas_data)

    return router
