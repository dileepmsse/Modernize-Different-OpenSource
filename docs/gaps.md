# Resolving Conflicts with Current State

When you encounter a conflict with the current state of your project, follow these steps:

1. **Identify the Conflict**  
  Use `git status` to see which files are in conflict.

2. **Open the Conflicted Files**  
  Look for conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) in the files.

3. **Manually Edit the Files**  
  Decide which changes to keep:  
  - Keep your changes  
  - Keep the incoming changes  
  - Or combine both

4. **Mark as Resolved**  
  After editing, run:
  ```bash
  git add <filename>
  ```

5. **Complete the Merge**  
  Finish the merge with:
  ```bash
  git commit
  ```

6. **Test Your Code**  
  Ensure everything works as expected.

---

**Tip:** Use a merge tool like VS Code, Meld, or `git mergetool` for easier conflict resolution.