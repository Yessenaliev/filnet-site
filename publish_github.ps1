# Publish the site to GitHub Pages (run via the .bat file)
$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot
$env:GIT_REDIRECT_STDERR = "2>&1"

$repo  = "filnet-site"
$owner = (gh api user --jq .login)
Write-Host "GitHub user: $owner"

if (-not (Test-Path ".git")) { git init -b main }
git config core.autocrlf false
New-Item -ItemType File -Path ".nojekyll" -Force | Out-Null
git add -A
git -c user.name="Filnet site" -c user.email="noreply@users.noreply.github.com" commit -m "Filnet site (draft)"

gh repo create $repo --public --source . --push --description "Filnet-Kazakhstan site (draft)"
if ($LASTEXITCODE -ne 0) {
  Write-Host "Repo may already exist, trying to push..."
  git remote remove origin 2>$null
  git remote add origin "https://github.com/$owner/$repo.git"
  git push -u origin main
}
gh api -X POST "repos/$owner/$repo/pages" -f "source[branch]=main" -f "source[path]=/"

Write-Host ""
Write-Host "REPOSITORY: https://github.com/$owner/$repo"
Write-Host "SITE (in 1-2 minutes): https://$owner.github.io/$repo/"
Write-Host "For colleagues: repository Settings -> Collaborators -> Add people"
