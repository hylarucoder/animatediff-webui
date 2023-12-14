from animatediff.app import current_app

app = current_app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, reload=True, host="0.0.0.0", port=7860)
