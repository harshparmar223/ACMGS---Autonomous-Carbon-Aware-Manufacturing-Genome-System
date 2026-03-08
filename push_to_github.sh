#!/usr/bin/env bash
# Quick Git Push Setup Script
# Run this to push your ACMGS project to GitHub

echo "========================================="
echo "ACMGS GitHub Push Setup"
echo "========================================="
echo ""

# Navigate to project directory
cd ACMGS---Autonomous-Carbon-Aware-Manufacturing-Genome-System-main

# Step 1: Configure Git (replace with your details)
echo "Step 1: Configure Git user"
read -p "Enter your GitHub username: " username
read -p "Enter your GitHub email: " email

git config user.name "$username"
git config user.email "$email"

echo "✓ Git configured for $username"
echo ""

# Step 2: Get repository URL
echo "Step 2: Set up GitHub repository"
echo ""
echo "Choose an option:"
echo "  A) I have an existing repository"
echo "  B) I want to create a new repository"
read -p "Enter choice (A/B): " choice

if [ "$choice" = "A" ] || [ "$choice" = "a" ]; then
    read -p "Enter your repository URL (https://github.com/username/repo.git): " repo_url
    git remote add origin "$repo_url"
    
elif [ "$choice" = "B" ] || [ "$choice" = "b" ]; then
    read -p "Enter repository name (e.g., ACMGS-Project): " repo_name
    echo ""
    echo "Please:"
    echo "  1. Go to: https://github.com/new"
    echo "  2. Create repository: $repo_name"
    echo "  3. Do NOT initialize with README/gitignore"
    echo ""
    read -p "Press Enter when done, then provide the repo URL: " 
    read -p "Repository URL: " repo_url
    git remote add origin "$repo_url"
fi

# Step 3: Push to GitHub
echo ""
echo "Step 3: Pushing to GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "========================================="
echo "✓ Successfully pushed to GitHub!"
echo "========================================="
echo "View your project at: $repo_url"
