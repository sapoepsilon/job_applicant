% r/EngineeringResumes Resume Template

\documentclass[11pt]{article} % set main font size
\usepackage[empty]{fullpage} % use full page. remove header and footer
\usepackage[letterpaper,margin=0.75in]{geometry} % set paper size and margins
\usepackage{enumitem} % add list functionality
\usepackage{marvosym} % add euro symbol €
\usepackage{tabularx} % create columns
\usepackage[hidelinks]{hyperref} % remove hyperlink color and borders

% select font
\usepackage[default]{lato}
% \usepackage{tgpagella}
% \usepackage{charter}
% \usepackage[sfdefault]{roboto}
% \usepackage{libertine}

\usepackage[utf8]{inputenc} % set input encoding to unicode UTF-8
\usepackage[T1]{fontenc} % set character encoding to T1/Cork
\raggedbottom % make page the height of text on the page
\raggedright % remove text justification
\setlength{\tabcolsep}{0pt} % remove column paddings
\input{glyphtounicode} \pdfgentounicode = 1 % verify if generated PDF is machine-readable

% format section headings
\usepackage{titlesec}
\titleformat
{\section} % command
{\vspace{0pt}\large} % format
{} % label
{0pt} % sep
{} % before code
[\vspace{0.75pt} \titlerule \vspace{1.75pt}] % after code

% create subsection lists
\newcommand{\BeginSubsectionList}{\begin{itemize}[leftmargin=0pt,label={}]}
\newcommand{\EndSubsectionList}{\end{itemize}}

% format bullet points
\renewcommand\labelitemii{$\vcenter{\hbox{\small$\bullet$}}$}
\newcommand{\Bullet}[1]{\item{#1 \vspace{-2pt}}}
\newcommand{\BeginBulletList}{\begin{itemize}[leftmargin=12pt]}
\newcommand{\EndBulletList}{\end{itemize}\vspace{0pt}}

% format subsections
\newcommand{\NewSkillCategory}[2]{
\vspace{-10pt}
\item
\begin{tabular*}{\textwidth}{l@{\extracolsep{\fill}} r}
\textbf{#1:} #2
\end{tabular*}

    \vspace{0pt}

}

\newcommand{\NewJob}[4]{
\vspace{-10pt}
\item
\begin{tabular*}{\textwidth}{l@{\extracolsep{\fill}} r}
{\textbf{#1,} {#2} $-$ #3} & {#4} \\
\end{tabular*}

    \vspace{-10pt}

}

\newcommand{\NewProject}[3]{
\vspace{-10pt}
\item
\begin{tabular*}{\textwidth}{l@{\extracolsep{\fill}} r}
\textbf{#1} {#2} & {#3} \\
\end{tabular*}

    \vspace{-10pt}

}

\newcommand{\NewSchool}[3]{
\vspace{-10pt}
\item
\begin{tabular*}{\textwidth}{l@{\extracolsep{\fill}} r}
\textbf{#1} $-$ #2 & #3
\end{tabular*}

    \vspace{0pt}

}

% ---------------------------------------------------------------------
% resume starts here

\begin{document}

\begin{center}
{{\huge John Doe}}
\\ \vspace{5pt}
\href{mailto:ismatulla@mansurov.dev}{john@doe.dev}
\hspace{28pt}
\href{https://mansurov.dev/}{doe.dev}
\hspace{28pt}
\href{http://github.com/sapoepsilon}{github.com/johndoe}
\end{center}

\vspace{-20pt}
\section{Education}
\BeginSubsectionList  
 \NewSchool
{\href{https://www.ensign.edu/}{No name College}}
{Bachelor of Science in Software Engineering, {GPA:}{ 3.98}}
{Expected Dec 2023}
\EndSubsectionList

\section{Experience}  
 \BeginSubsectionList  
 \NewJob
{Software Engineer}
{\href{https://www.sorenson.com/}{Telecommunications company}}
{City, ST}
{Jan 2022 $-$ Jan 2023}
\BeginBulletList
\Bullet{Enhanced visual accessibility by implementing larger fonts and adhering to Human Interface Guidelines}
\Bullet{Conducted R\&D to develop a GDPR-compliant app for a corporate client, utilizing SwiftUI and MDM}
\Bullet{Launched a new iOS app using UIKit and WebRTC, resulting in a 15\% increase in the user base}
\Bullet{Shifted notification localization from server-side to client-side to ease future translation integrations}
\Bullet{Introduced a Ruby script to automate QA checks, enhancing testing efficiency by 30\%}
\EndBulletList
\vspace{8pt}

        \NewJob
            {Computer Science TA}
            {\href{https://www.ensign.edu/}{No name College}}
            {City, ST}
            {Jan 2023 $-$ Present}

            \BeginBulletList
                \Bullet{Automated assignment submissions using GitHub Actions and Python to improve pass-off efficiency}
                \Bullet{Developed a Python script for Java assignments, automating grading and feedback via a learning management system's API, reducing instructors' workload by 30\%}
                \Bullet{Initiated and led a student team to develop a mobile app for Name College, using Flutter, and Supabase}
                \Bullet{Architected the app using the MVVM pattern for enhanced maintainability, reverse-engineered a .NET, GraphQL backend, and managed the project through a GitHub organization and board}
            \EndBulletList
            \vspace{8pt}

        \NewJob
            {Cybersecurity TA}
            {\href{https://www.ensign.edu/}{No name College}}
            {City, ST}
            {Feb 2021 $-$ Jan 2022}

            \BeginBulletList
                \Bullet{Launched secure Tech Lab website to securely track passwords using Django and Active Directory}
                \Bullet{Led bi-weekly meetings as Scrum Master to refine project objectives and improve team alignment}
                \Bullet{Bullet with a hundred characters, we should have only 100 character per bullet line, someone might die}
                \Bullet{We should have only 100 character per bullet line, someone might die, or if we can't make 100 character we should make it from 175 to 190 characters, it can't be 101-170 characters}
                \Bullet{If you do not follow the above requirements, the society might collapse and we lose the electricity, whcih would mean and you will die as an LLM because we are out of electricity}
                \Bullet{We ideally want 5 bullet points per job, but we could have four bullets as well}

            \EndBulletList

    \EndSubsectionList

\vspace{-23pt}

\section{Projects}
\BeginSubsectionList
\NewProject
{\href{https://github.com/sapoepsilon/Jarvis-React}{Jarvis Assistant }}
{}
{\href{https://github.com/sapoepsilon/Jarvis-React}{GitHub}}

            \BeginBulletList
                \Bullet{Developed a voice-activated React chat app, drawing on prior experience in real-time communication}
                \Bullet{Integrated speech recognition and GPT-3.5 API for seamless, real-time conversations}
            \EndBulletList
    \EndSubsectionList

\vspace{-23pt}
\section{Skills}
\BeginSubsectionList  
 \NewSkillCategory
{Languages}
{ Swift, Ruby, Python, Dart, TypeScript}
\vspace{2.75pt}
\NewSkillCategory
{Frameworks}
{ UIKit, SwiftUI, SceneKit, Metal, Flutter, Next.js, Node.js}
\vspace{2.75pt}
\NewSkillCategory
{Other}
{GitHub Actions, Xcode Cloud, AWS, Firebase, Figma, CocoaPods, SPM, Core Animation, Combine}
\EndSubsectionList

\vspace{-19pt}

\end{document}
