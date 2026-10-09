"""
GapWise - AI Study Assistant That Detects Learning Gaps
Run this single Python file in VS Code:
    python gapwise.py

Uses only Python's standard library (Tkinter).
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox

QUESTION_BANK = [
    {"subject": "Math", "skill": "Algebra", "question": "Solve for x: 3x + 6 = 21",
     "options": ["3", "5", "7", "9"], "answer": 1,
     "explanation": "Subtract 6 to get 3x = 15, then divide by 3. Therefore x = 5."},
    {"subject": "Math", "skill": "Algebra", "question": "Which expression is equivalent to 2(x + 4)?",
     "options": ["2x + 4", "2x + 6", "2x + 8", "x + 8"], "answer": 2,
     "explanation": "Multiply both x and 4 by 2, producing 2x + 8."},
    {"subject": "Math", "skill": "Fractions", "question": "What is 3/4 + 1/8?",
     "options": ["4/12", "7/8", "1", "5/8"], "answer": 1,
     "explanation": "Convert 3/4 to 6/8. Then 6/8 + 1/8 = 7/8."},
    {"subject": "Math", "skill": "Fractions", "question": "What is 2/3 of 18?",
     "options": ["6", "9", "12", "15"], "answer": 2,
     "explanation": "Divide 18 by 3 to get 6, then multiply by 2 to get 12."},
    {"subject": "Science", "skill": "Cell Biology", "question": "Which organelle is primarily responsible for producing ATP?",
     "options": ["Nucleus", "Mitochondrion", "Ribosome", "Golgi apparatus"], "answer": 1,
     "explanation": "Mitochondria generate most cellular ATP through cellular respiration."},
    {"subject": "Science", "skill": "Cell Biology", "question": "What is the main function of ribosomes?",
     "options": ["Store DNA", "Produce proteins", "Break down glucose", "Control cell movement"], "answer": 1,
     "explanation": "Ribosomes assemble amino acids into proteins."},
    {"subject": "Science", "skill": "Physics", "question": "What happens to acceleration if force doubles and mass stays constant?",
     "options": ["It halves", "It stays constant", "It doubles", "It becomes zero"], "answer": 2,
     "explanation": "Newton's second law is F = ma. With constant mass, doubling force doubles acceleration."},
    {"subject": "Science", "skill": "Physics", "question": "Which unit measures electrical current?",
     "options": ["Volt", "Watt", "Ampere", "Ohm"], "answer": 2,
     "explanation": "Electrical current is measured in amperes (amps)."},
    {"subject": "Computing", "skill": "Programming Logic", "question": "What does a loop do in a computer program?",
     "options": ["Repeats instructions", "Deletes variables", "Stops the computer", "Encrypts all data"], "answer": 0,
     "explanation": "A loop repeatedly executes instructions while a condition or sequence applies."},
    {"subject": "Computing", "skill": "Programming Logic", "question": "Which value type represents true or false?",
     "options": ["String", "Boolean", "Array", "Float"], "answer": 1,
     "explanation": "A Boolean value represents true or false."},
    {"subject": "Computing", "skill": "Data Structures", "question": "Which data structure follows First In, First Out?",
     "options": ["Stack", "Queue", "Tree", "Set"], "answer": 1,
     "explanation": "A queue removes elements in the order they were inserted: FIFO."},
    {"subject": "Computing", "skill": "Data Structures", "question": "Which structure stores key-value pairs?",
     "options": ["Hash map", "Queue", "Linked list", "Stack"], "answer": 0,
     "explanation": "A hash map associates keys with corresponding values."},
]


class GapWiseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GapWise - AI Study Assistant")
        self.root.geometry("1100x760")
        self.root.minsize(850, 650)
        self.root.configure(bg="#f4f7fc")

        self.skill_state = {}
        for q in QUESTION_BANK:
            self.skill_state.setdefault(q["skill"], {
                "subject": q["subject"], "correct": 0, "attempted": 0
            })
        self.total_correct = 0
        self.total_answered = 0
        self.current_questions = QUESTION_BANK.copy()
        self.current_index = 0
        self.selected = tk.IntVar(value=-1)
        self.answer_checked = False

        self._build_ui()
        self.render_dashboard()
        self.render_question()

    def _build_ui(self):
        style = ttk.Style()
        style.configure("TCombobox", padding=5)
        outer = tk.Frame(self.root, bg="#f4f7fc")
        outer.pack(fill="both", expand=True, padx=18, pady=18)

        sidebar = tk.Frame(outer, bg="#17132f", width=190)
        sidebar.pack(side="left", fill="y", padx=(0, 18))
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="◆  GapWise", bg="#17132f", fg="white",
                 font=("Segoe UI", 18, "bold")).pack(pady=(25, 28))
        self._button(sidebar, "Dashboard", lambda: self.scroll_to(self.quiz_panel))
        self._button(sidebar, "Diagnostic Quiz", lambda: self.scroll_to(self.quiz_panel))
        self._button(sidebar, "Study Plan", lambda: self.scroll_to(self.plan_panel))
        tk.Label(sidebar, text="How it works\n\nTopics below 60% mastery\nare flagged as learning gaps\nand prioritized in your plan.",
                 bg="#211c42", fg="#d4d0e8", wraplength=155, justify="left",
                 padx=12, pady=14).pack(side="bottom", fill="x", padx=12, pady=16)

        content = tk.Frame(outer, bg="#f4f7fc")
        content.pack(side="left", fill="both", expand=True)
        header = tk.Frame(content, bg="#f4f7fc")
        header.pack(fill="x", pady=(0, 15))
        tk.Label(header, text="AI Study Assistant", bg="#f4f7fc", fg="#182033",
                 font=("Segoe UI", 24, "bold")).pack(side="left")
        self._button(header, "Reset progress", self.reset_progress, secondary=True).pack(side="right")

        stats = tk.Frame(content, bg="#f4f7fc")
        stats.pack(fill="x", pady=(0, 14))
        self.stat_labels = {}
        for key, label in [("answered", "Questions answered"), ("accuracy", "Accuracy"),
                           ("gaps", "Learning gaps"), ("mastered", "Mastered skills")]:
            card = tk.Frame(stats, bg="white", highlightbackground="#e2e7f2", highlightthickness=1)
            card.pack(side="left", fill="both", expand=True, padx=4)
            tk.Label(card, text=label.upper(), bg="white", fg="#657089",
                     font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=10, pady=(12, 2))
            value = tk.Label(card, text="0", bg="white", fg="#182033",
                             font=("Segoe UI", 20, "bold"))
            value.pack(anchor="w", padx=10, pady=(0, 12))
            self.stat_labels[key] = value

        body = tk.Frame(content, bg="#f4f7fc")
        body.pack(fill="both", expand=True)
        left = tk.Frame(body, bg="#f4f7fc")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right = tk.Frame(body, bg="#f4f7fc", width=270)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        self.quiz_panel = self._panel(left, "Diagnostic Quiz")
        selector_row = tk.Frame(self.quiz_panel, bg="white")
        selector_row.pack(fill="x", pady=(0, 8))
        tk.Label(selector_row, text="Subject:", bg="white", fg="#182033").pack(side="left")
        self.subject = tk.StringVar(value="Mixed topics")
        combo = ttk.Combobox(selector_row, textvariable=self.subject, state="readonly",
                             values=["Mixed topics", "Math", "Science", "Computing"], width=18)
        combo.pack(side="right")
        combo.bind("<<ComboboxSelected>>", lambda _e: self.filter_questions())

        self.progress = tk.StringVar()
        self.score = tk.StringVar()
        progress_row = tk.Frame(self.quiz_panel, bg="white")
        progress_row.pack(fill="x")
        tk.Label(progress_row, textvariable=self.progress, bg="white", fg="#657089").pack(side="left")
        tk.Label(progress_row, textvariable=self.score, bg="white", fg="#657089").pack(side="right")
        self.progress_bar = ttk.Progressbar(self.quiz_panel, maximum=100)
        self.progress_bar.pack(fill="x", pady=(8, 18))

        self.question_topic = tk.Label(self.quiz_panel, text="", bg="#efedff", fg="#4b3ed0",
                                       font=("Segoe UI", 9, "bold"), padx=8, pady=5)
        self.question_topic.pack(anchor="w", pady=(0, 10))
        self.question_text = tk.Label(self.quiz_panel, text="", bg="white", fg="#182033",
                                      font=("Segoe UI", 14, "bold"), wraplength=520,
                                      justify="left", anchor="w")
        self.question_text.pack(fill="x", pady=(0, 12))
        self.options_frame = tk.Frame(self.quiz_panel, bg="white")
        self.options_frame.pack(fill="x")
        self.feedback = tk.Label(self.quiz_panel, text="", bg="#f7f9ff", fg="#4b5570",
                                 wraplength=520, justify="left", padx=10, pady=8)
        self.feedback.pack(fill="x", pady=(8, 8))
        actions = tk.Frame(self.quiz_panel, bg="white")
        actions.pack(fill="x", pady=(8, 0))
        self.skip_btn = tk.Button(actions, text="Skip", command=self.skip_question)
        self.skip_btn.pack(side="left")
        self.submit_btn = tk.Button(actions, text="Check answer", command=self.check_answer,
                                    bg="#6658e8", fg="white", activebackground="#4b3ed0",
                                    relief="flat", padx=12, pady=8)
        self.submit_btn.pack(side="right", padx=(6, 0))
        self.next_btn = tk.Button(actions, text="Next question", command=self.next_question,
                                  bg="#6658e8", fg="white", relief="flat", padx=12, pady=8)
        self.next_btn.pack(side="right")

        self.plan_panel = self._panel(left, "Personalized Study Plan")
        self.plan_list = tk.Frame(self.plan_panel, bg="white")
        self.plan_list.pack(fill="x")

        mastery_panel = self._panel(right, "Skill Mastery")
        self.mastery_list = tk.Frame(mastery_panel, bg="white")
        self.mastery_list.pack(fill="x")
        self.insight = tk.Label(mastery_panel, text="", bg="#f6f3ff", fg="#51478d",
                                wraplength=220, justify="left", padx=10, pady=10)
        self.insight.pack(fill="x", pady=(12, 0))

        gaps_panel = self._panel(right, "Detected Gaps")
        self.gap_list = tk.Frame(gaps_panel, bg="white")
        self.gap_list.pack(fill="x")

    def _button(self, parent, text, command, secondary=False):
        button = tk.Button(parent, text=text, command=command, relief="flat", padx=10, pady=8,
                           bg="white" if secondary else "#2d2850",
                           fg="#182033" if secondary else "white",
                           activebackground="#4b3ed0")
        button.pack(fill="x", padx=10, pady=4)
        return button

    def _panel(self, parent, title):
        panel = tk.Frame(parent, bg="white", highlightbackground="#e2e7f2", highlightthickness=1)
        panel.pack(fill="x", pady=(0, 14), ipadx=14, ipady=12)
        tk.Label(panel, text=title, bg="white", fg="#182033",
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=14, pady=(8, 12))
        return panel

    def scroll_to(self, widget):
        widget.focus_set()

    def mastery_for(self, skill):
        data = self.skill_state[skill]
        return round(data["correct"] / data["attempted"] * 100) if data["attempted"] else 0

    def get_gaps(self):
        gaps = []
        for skill, data in self.skill_state.items():
            if data["attempted"]:
                mastery = self.mastery_for(skill)
                if mastery < 60:
                    gaps.append({"skill": skill, "subject": data["subject"],
                                 "mastery": mastery, "attempted": data["attempted"]})
        return sorted(gaps, key=lambda item: item["mastery"])

    def render_question(self):
        if self.current_index >= len(self.current_questions):
            self.finish_quiz()
            return
        self.answer_checked = False
        self.selected.set(-1)
        item = self.current_questions[self.current_index]
        self.question_topic.config(text=f'{item["subject"]} - {item["skill"]}')
        self.question_text.config(text=item["question"])
        self.progress.set(f"Question {self.current_index + 1} of {len(self.current_questions)}")
        self.score.set(f"Score: {self.total_correct}")
        self.progress_bar["value"] = self.current_index / len(self.current_questions) * 100
        for child in self.options_frame.winfo_children():
            child.destroy()
        for i, option in enumerate(item["options"]):
            tk.Radiobutton(self.options_frame, text=f"{chr(65+i)}. {option}", variable=self.selected,
                           value=i, bg="white", fg="#182033", activebackground="white",
                           selectcolor="#efedff", anchor="w", justify="left",
                           font=("Segoe UI", 10), wraplength=520).pack(fill="x", pady=4)
        self.feedback.config(text="")
        self.submit_btn.config(state="normal")
        self.skip_btn.config(state="normal")
        self.next_btn.pack_forget()
        self.submit_btn.pack(side="right", padx=(6, 0))
        self.skip_btn.pack(side="left")

    def check_answer(self):
        if self.selected.get() < 0 or self.answer_checked:
            messagebox.showinfo("Choose an answer", "Please select an option first.")
            return
        self.answer_checked = True
        item = self.current_questions[self.current_index]
        correct = self.selected.get() == item["answer"]
        data = self.skill_state[item["skill"]]
        data["attempted"] += 1
        self.total_answered += 1
        if correct:
            data["correct"] += 1
            self.total_correct += 1
            result = "Correct!"
        else:
            result = f'Not quite. Correct answer: {item["options"][item["answer"]]}'
        self.feedback.config(text=f'{result} {item["explanation"]}')
        self.submit_btn.pack_forget()
        self.next_btn.pack(side="right")
        self.skip_btn.config(state="disabled")
        self.render_dashboard()

    def next_question(self):
        self.current_index += 1
        self.render_question()

    def skip_question(self):
        self.current_index += 1
        self.render_question()

    def finish_quiz(self):
        self.progress.set("Diagnostic complete")
        self.progress_bar["value"] = 100
        for child in self.options_frame.winfo_children():
            child.destroy()
        self.question_topic.config(text="Results")
        self.question_text.config(text="Quiz completed! Your learning gaps and study plan are ready.")
        self.feedback.config(text=f"Overall accuracy: {round(self.total_correct / self.total_answered * 100) if self.total_answered else 0}%.")
        self.submit_btn.pack_forget()
        self.skip_btn.pack_forget()
        self.next_btn.pack_forget()
        self.render_dashboard()

    def filter_questions(self):
        subject = self.subject.get()
        self.current_questions = QUESTION_BANK.copy() if subject == "Mixed topics" else [
            q for q in QUESTION_BANK if q["subject"] == subject
        ]
        self.current_index = 0
        self.render_question()

    def render_dashboard(self):
        accuracy = round(self.total_correct / self.total_answered * 100) if self.total_answered else 0
        attempted_skills = [s for s, d in self.skill_state.items() if d["attempted"]]
        gaps = self.get_gaps()
        mastered = [s for s in attempted_skills if self.mastery_for(s) >= 80]
        self.stat_labels["answered"].config(text=str(self.total_answered))
        self.stat_labels["accuracy"].config(text=f"{accuracy}%")
        self.stat_labels["gaps"].config(text=str(len(gaps)))
        self.stat_labels["mastered"].config(text=str(len(mastered)))

        for child in self.mastery_list.winfo_children():
            child.destroy()
        for skill, data in self.skill_state.items():
            mastery = self.mastery_for(skill)
            label = f"{mastery}%" if data["attempted"] else "Not assessed"
            tk.Label(self.mastery_list, text=f"{skill}: {label}", bg="white", fg="#182033",
                     anchor="w", wraplength=230).pack(fill="x", pady=3)
            bar = ttk.Progressbar(self.mastery_list, maximum=100, value=mastery)
            bar.pack(fill="x", pady=(0, 7))

        for child in self.gap_list.winfo_children():
            child.destroy()
        if not gaps:
            tk.Label(self.gap_list, text="No confirmed gaps yet. Answer questions to produce a diagnosis.",
                     bg="white", fg="#657089", wraplength=220, justify="left").pack(fill="x")
        else:
            for gap in gaps:
                priority = "HIGH PRIORITY" if gap["mastery"] < 40 else "NEEDS REVIEW"
                tk.Label(self.gap_list,
                         text=f'{gap["skill"]}\n{gap["mastery"]}% mastery after {gap["attempted"]} attempt(s)\n{priority}',
                         bg="#f7f9ff", fg="#a82f3e" if gap["mastery"] < 40 else "#9b6513",
                         justify="left", wraplength=220, padx=8, pady=8).pack(fill="x", pady=4)

        for child in self.plan_list.winfo_children():
            child.destroy()
        if not self.total_answered:
            plan_text = "Your study plan will appear after you answer diagnostic questions."
            tk.Label(self.plan_list, text=plan_text, bg="white", fg="#657089",
                     wraplength=520, justify="left").pack(anchor="w")
        elif not gaps:
            tk.Label(self.plan_list,
                     text="Maintain your progress: review topics for 15 minutes and try harder mixed questions.",
                     bg="white", fg="#182033", wraplength=520, justify="left").pack(anchor="w", pady=4)
        else:
            for i, gap in enumerate(gaps[:3], 1):
                minutes = 30 if gap["mastery"] < 40 else 20
                tk.Label(self.plan_list,
                         text=f'Day {i}: {gap["skill"]} — Spend {minutes} minutes reviewing fundamentals, '
                              f'study two worked examples, then complete five practice questions. Target: 80%.',
                         bg="white", fg="#182033", wraplength=520, justify="left",
                         anchor="w").pack(fill="x", pady=5)

        if not attempted_skills:
            insight = "Complete a few questions so the assistant can detect patterns in your understanding."
        elif gaps:
            weak = gaps[0]
            insight = f'Learning pattern: {weak["skill"]} is your largest detected gap at {weak["mastery"]}%. Review foundational examples first.'
        else:
            insight = f'Learning pattern: Your assessed topics are stable. {len(mastered)} skill(s) are currently at mastery level.'
        self.insight.config(text=insight)

    def reset_progress(self):
        if messagebox.askyesno("Reset progress", "Clear all quiz progress?"):
            for data in self.skill_state.values():
                data["correct"] = 0
                data["attempted"] = 0
            self.total_correct = 0
            self.total_answered = 0
            self.current_questions = QUESTION_BANK.copy()
            self.current_index = 0
            self.subject.set("Mixed topics")
            self.render_dashboard()
            self.render_question()


if __name__ == "__main__":
    root = tk.Tk()
    app = GapWiseApp(root)
    root.mainloop()
