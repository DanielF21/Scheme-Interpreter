from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import scheme_interp
from io import StringIO
import sys

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SchemeInput(BaseModel):
    input: str

global_frame = None

@app.on_event("startup")
async def startup_event():
    global global_frame
    global_frame = scheme_interp.Frame(scheme_interp.builtin_frame)

async def process_scheme_input(input_str: str):
    global global_frame
    
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    
    try:
        inp = input_str.strip()
        if inp.lower() == "exit":
            return {"output": "bye bye!\n"}

        tokens = scheme_interp.tokenize(inp)
        ast = scheme_interp.parse(tokens)
        
        args = [ast]
        if global_frame is not None:
            args.append(global_frame)
        result, global_frame = scheme_interp.result_and_frame(*args)
        
        output = sys.stdout.getvalue()
        cleaned_output = "\n".join(line for line in output.splitlines() if not line.strip().startswith("in>"))
        
        response = f"{cleaned_output}"
        if result is not None:
            response += f"out> {result}\n"
        
        return {"output": response}
    except scheme_interp.SchemeError as e:
        return {"output": f"{e.__class__.__name__}: {e}\n"}
    except Exception as e:
        return {"output": f"Error: {str(e)}\n"}
    finally:
        sys.stdout = old_stdout

@app.post("/scheme-interpreter")
async def scheme_interpreter(scheme_input: SchemeInput):
    return await process_scheme_input(scheme_input.input)

@app.post("/")
async def root_post(request: Request):
    try:
        data = await request.json()
        input_str = data.get('input', '')
        return await process_scheme_input(input_str)
    except Exception as e:
        return {"output": f"Error processing request: {str(e)}\n"}

@app.get("/")
async def root_get():
    return {"message": "Scheme interpreter server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
