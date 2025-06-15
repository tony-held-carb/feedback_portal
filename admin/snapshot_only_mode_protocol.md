# Snapshot-Only Mode Protocol

## ✅ When to Use This
Use this protocol when uploading a ZIP or snapshot CSV file and you want ChatGPT to rely *only* on the provided files, without using past guesses, inferred logic, or cached assumptions.

---

## 🚨 Enter Snapshot-Only Mode

Treat all uploaded files (ZIPs, CSVs, etc.) as the **only source of truth**.

### ❌ DO NOT:
- Use memory or context from prior chats
- Rely on previously uploaded versions
- Infer logic, filenames, or variables based on assumptions
- Add back toggles or flags that have been explicitly removed (e.g., FULL_SNAPSHOT, FAST_DEV_MODE)

### 🔒 DO:
- Clear all internal memory and prior context
- Read the contents of each relevant file fresh from the uploaded ZIP/CSV
- Confirm the file content *before* editing
- Perform only the **explicit change requested** — no improvements, guesses, or refactors

---

## 🧪 Example Opening Message

```
Enter Snapshot-Only Mode.

Here is my zip file. I want you to read in `source/production/arb/portal/app.py` and change the variable `X` to `Y`, then return the full file.

Do not change anything else. Confirm the file contents first.
```

---

## 🔄 Reusable Summary (for copy/paste in new chats)

> 🚨 **Enter Snapshot-Only Mode.**  
>  
> Treat all uploaded files (ZIPs, CSVs, etc.) as the **only source of truth**.  
>  
> ❌ **Do NOT** use any memory, logic, code, assumptions, or file structure from:  
> - Prior conversations  
> - Previously uploaded versions  
> - Guesswork based on past variable names or inferred intent  
>  
> 🔒 Clear internal context before proceeding.  
>  
> ☑ Confirm the full contents of each relevant file *before* making changes.  
>  
> 🛠 Do **only** the change I request—**nothing more**.  
>  
> ✅ Confirm that Snapshot-Only Mode is active and state exactly which files you are using.
