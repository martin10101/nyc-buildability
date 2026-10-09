# Owner guide: turning on the five loops (plain English)

This is the short list of commands to type to start the five work loops. You type
each line in the Claude chat, starting with `!`. Do them in order. After each one,
read the last line it prints.

There are five steps. Steps 1 and 2 set up the shared program. Steps 3 and 4 start
the first loop as a careful test. Step 5 starts the other loops. Wait for the
assistant to say "go ahead" before step 5.

The commands are long but you only paste them. Nothing here changes your files or
settings on its own; each command checks itself and stops if anything looks wrong.

---

## Step 1 - Check (safe, changes nothing)

Type this:

```
!powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\controller_update\commission_lanes.ps1 -Phase check
```

What good looks like: the last line says `CHECK PASSED`.

If any line starts with `STOP`: stop here and tell the assistant what it said. Do
not run the next step.

## Step 2 - Update (sets up the program and prepares all five loops)

Type this:

```
!powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\controller_update\commission_lanes.ps1 -Phase update
```

What good looks like: the last line says `UPDATE PASSED`.

If any line starts with `STOP`: stop and tell the assistant. Do not run the next
step.

## Step 3 - Start the first loop as a test (the "canary")

The assistant will give you two values to paste in: a folder path and a short task
name. Put them where it says `<folder>` and `<task-name>` below, then type the line:

```
!powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\controller_update\commission_lanes.ps1 -Phase lane -Lane 1 -Worktree <folder> -PacketId <task-name>
```

What good looks like: it prints `started DETACHED` and a line that says the loop
will wait for you to approve it. (This step does NOT print the approval code - the
loop starts in the background and parks; step 4 shows you the code.)

If any line starts with `STOP`: stop and tell the assistant.

## Step 4 - Approve the first loop (two commands)

You run the approve command twice. The first time shows you the code; the second
time uses it.

First, run it WITHOUT a code. Use the same folder and task name as step 3:

```
!powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\controller_update\commission_lanes.ps1 -Phase approve -Lane 1 -Worktree <folder> -PacketId <task-name>
```

This one prints the loop's pending approval, including a long code called a
"digest", and then stops on purpose with exactly this line:

```
STOP [approve]: pass -PromptDigest <the digest printed above> to approve the held prompt
```

That one STOP is expected here - it is just showing you the code. Copy the long
code it printed just above that line.

Now run the SAME command again, this time pasting the code after `-PromptDigest`:

```
!powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\controller_update\commission_lanes.ps1 -Phase approve -Lane 1 -Worktree <folder> -PacketId <task-name> -PromptDigest <digest>
```

What good looks like: it prints `approved` and then `canary re-started`.

If the second command (or any command other than that expected first-approve line
above) prints a line starting with `STOP`: stop and tell the assistant.

Now wait. The assistant watches this first loop finish one round of work and checks
it is healthy. The assistant will tell you either "the canary passed - go ahead" or
that something went wrong and it is stopping.

## Step 5 - Start the other loops (only after the assistant says "go ahead")

The assistant will give you one file path (a small plan it wrote). Paste it where it
says `<plan-file>`:

```
!powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\controller_update\commission_lanes.ps1 -Phase lanes -PlanFile <plan-file>
```

What good looks like: the last line says `LANES STARTED`. The loops start one at a
time, a minute apart. Once this finishes, up to five loops are running.

If any line starts with `STOP`: stop and tell the assistant.

---

## The one rule to remember

If any command prints a line that begins with `STOP`, stop and tell the assistant
exactly what it said. A `STOP` means the command found something not as expected and
did nothing further, on purpose. This is safe - it is the command protecting the work.

The ONE exception is the first approve command in step 4: it stops on purpose with
`STOP [approve]: pass -PromptDigest ...` only to show you the code to copy. For that
one, copy the code and run the approve command again with it (as step 4 explains). If
you are ever unsure whether a STOP is that expected one, tell the assistant.

## Why sometimes fewer than five loops run

Five is the goal. Sometimes the assistant will run four, three, or fewer, and it will
tell you why in plain words - for example, the computer is low on free space, or there
is not enough separate work ready to fill five loops without them bumping into each
other. If that happens, the assistant reduces the number one step at a time and tells
you the reason.
