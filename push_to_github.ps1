# ACMGS GitHub Push Guide (Windows PowerShell)
# Follow these steps to push your project to GitHub

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "ACMGS GitHub Push Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to project directory
Set-Location ACMGS---Autonomous-Carbon-Aware-Manufacturing-Genome-System-main

# Step 1: Configure Git
Write-Host "Step 1: Configure Git User" -ForegroundColor Yellow
$username = Read-Host "Enter your GitHub username"
$email = Read-Host "Enter your GitHub email"

git config user.name "$username"
git config user.email "$email"

Write-Host "✓ Git configured for $username" -ForegroundColor Green
Write-Host ""

# Step 2: Set up repository
Write-Host "Step 2: GitHub Repository" -ForegroundColor Yellow
Write-Host ""
Write-Host "Options:"
Write-Host "  A) I have an existing repository"
Write-Host "  B) I want to create a new repository"
$choice = Read-Host "Enter choice (A/B)"

if ($choice -eq "A" -or $choice -eq "a") {
    $repoUrl = Read-Host "Enter your repository URL (https://github.com/username/repo.git)"
    git remote add origin $repoUrl
} 
elseif ($choice -eq "B" -or $choice -eq "b") {
    $repoName = Read-Host "Enter new repository name (e.g., ACMGS-Project)"
    Write-Host ""
    Write-Host "Please create the repository on GitHub:" -ForegroundColor Yellow
    Write-Host "  1. Go to: https://github.com/new" -ForegroundColor White
    Write-Host "  2. Repository name: $repoName" -ForegroundColor White
    Write-Host "  3. Keep it Public or Private (your choice)" -ForegroundColor White
    Write-Host "  4. Do NOT initialize with README, .gitignore, or license" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter when repository is created"
    
    $repoUrl = "https://github.com/$username/$repoName.git"
    Write-Host "Using URL: $repoUrl" -ForegroundColor White
    git remote add origin $repoUrl
}

# Step 3: Push to GitHub
Write-Host ""
Write-Host "Step 3: Pushing to GitHub..." -ForegroundColor Yellow
git branch -M main
git push -u origin main

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "✓ Successfully pushed to GitHub!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "View at: $repoUrl" -ForegroundColor White
