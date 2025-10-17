#!/bin/bash

# Load environment variables
export $(cat .env | xargs)

# Start both servers with concurrently
npm run dev
