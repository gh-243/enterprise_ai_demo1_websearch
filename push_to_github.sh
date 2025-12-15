#!/bin/bash
# Script to push to your own GitHub repository

echo "🚀 Setting up your own GitHub repository"
echo ""
echo "Step 1: Create a new repository on GitHub"
echo "  - Go to: https://github.com/new"
echo "  - Repository name: ai_chatbot (or any name you prefer)"
echo "  - Description: Enterprise AI chatbot with web search and cost tracking"
echo "  - Make it Public or Private (your choice)"
echo "  - DO NOT initialize with README (we already have one)"
echo ""
echo "Step 2: After creating the repository, replace YOUR_USERNAME below:"
echo ""

# Replace YOUR_USERNAME with your actual GitHub username
read -p "Enter your GitHub username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ Username cannot be empty"
    exit 1
fi

echo ""
echo "Step 3: Updating remote origin..."
git remote remove origin
git remote add origin "https://github.com/$GITHUB_USERNAME/ai_chatbot.git"

echo ""
echo "Step 4: Pushing to your repository..."
git push -u origin main

echo ""
echo "✅ Done! Your repository is at:"
echo "   https://github.com/$GITHUB_USERNAME/ai_chatbot"
