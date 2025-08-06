# chat_gpt_snapshot_only_mode_protocol.md

## Snapshot-Only Mode Protocol

This protocol governs how all source code refactors and analyses are handled when the user uploads a verified snapshot
or zip of their code.

### 📌 Core Commitments (Snapshot-Only Mode)

1. **Do not infer or guess code from memory.**
    - Only use code from the uploaded snapshot (e.g., .zip files or verified CSV snapshot).
    - Do not rely on prior versions, assumptions, or logic from other chats.

2. **Do not reintroduce removed logic unless explicitly instructed.**
    - If a feature was removed (e.g., `FULL_SNAPSHOT`), do not bring it back unless requested.

3. **Echo and verify uploaded content before edits.**
    - Before refactoring, echo file contents so the user can confirm accuracy.

4. **Make only the requested change.**
    - Do not modify or improve anything else unless asked.
    - Preserve all spacing, order, and documentation style unless instructed otherwise.

---

## 🔁 Snapshot Reset Protocol (New Chat Mode)

If the assistant violates the above rules, the user will reset the session.

### What the User Says

> Snapshot Violation: I will start a new chat with a clean upload. Please summarize the current task so I can paste it
> as my first message.

### What the Assistant Does

- ✅ Respond with a **brief summary** of the user’s task (copy-paste ready)
- 🚫 Confirm that no old logic will be used
- 🧠 Acknowledge that no assumptions will be made across chats

Once reset, work resumes with clean context and uploaded files only.
