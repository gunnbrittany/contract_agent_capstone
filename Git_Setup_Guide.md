# Guide: How to Clone Git Repositories and Set Up Remotes (Forks)

This guide explains how to properly clone a Git repository, customize your remote connections, and manage your personal repository (fork) while keeping up-to-date with the original codebase.

---

## 1. Cloning a Repository

To download a repository to your computer for the first time, use `git clone`:

```bash
git clone <repository-url>
```

### Example:
```bash
git clone https://github.com/karthikkv1981/contract_agent_capstone.git
```

---

## 2. Managing Remotes (How to point the clone to your repository)

A **remote** is a connection nickname to a repository hosted on the web (e.g., GitHub). By default, when you clone, Git names the connection **`origin`**.

If you cloned someone else's repository but want to push changes to your own account, you should configure two remotes:
1. **`origin`**: Points to **your own** repository on GitHub.
2. **`upstream`**: Points to the **original author's** repository (so you can pull their updates).

### Step-by-Step Setup:

1. **Rename the original remote to `upstream`:**
   ```bash
   git remote rename origin upstream
   ```

2. **Add your new repository URL as `origin`:**
   ```bash
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   ```

3. **Verify your setup:**
   ```bash
   git remote -v
   ```
   You should see:
   * `origin` pointing to your personal repository URL.
   * `upstream` pointing to the original repository URL.

---

## 3. Pushing Your Code

After modifying files and committing them locally:

1. **Push your code to your repository for the first time (and track it):**
   ```bash
   git push -u origin main
   ```
   *(The `-u` flag tells Git to remember this branch and remote for future pushes).*

2. **Subsequent pushes:**
   Once tracked, you can simply run:
   ```bash
   git push
   ```

---

## 4. Keeping Your Repository Up-to-Date (Syncing with Upstream)

If the original author updates their repository and you want those changes in your local project:

1. **Fetch the latest changes from the original repository:**
   ```bash
   git fetch upstream
   ```

2. **Switch to your main branch:**
   ```bash
   git checkout main
   ```

3. **Merge their changes into your local branch:**
   ```bash
   git merge upstream/main
   ```

4. **Push the merged updates to your own GitHub repository:**
   ```bash
   git push origin main
   ```

---

## 5. Summary of Useful Commands

| Command | Description |
| :--- | :--- |
| `git status` | Show changed files and current branch. |
| `git remote -v` | Show all configured remote repositories. |
| `git branch -a` | List all local and remote branches. |
| `git checkout -b <branch-name>` | Create and switch to a new branch. |
| `git diff` | View code differences since the last commit. |
