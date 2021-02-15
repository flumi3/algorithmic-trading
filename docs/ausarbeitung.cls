%%-*- LaTeX -*-%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% Ausarbeitung.cls
%
% Klassendatei fuer Projektarbeiten, Bachelorarbeiten, Masterarbeiten, Praxisberichte
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Title:			ausarbeitung.cls
% Author:			Ulrich Klauck, Manuel Blum (HTW Aalen)
% Credits to:		Matthias Müller <matthias.mueller@htw-aalen.de>, Prof. Schiefer
% Modifiied by:		Sebastian Stigler    
% Date:			2008/12/4
% Last Rev.:		2016/12/01
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Identify the class.
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ausarbeitung}[2008/07/02 Ausarbeitung HS Aalen]

\PassOptionsToClass{%
	12pt, % Schriftgröße [10pt, 11pt, 12pt]
	a4paper, % Papierformat [a4paper, a5paper, b5paper, letterpaper, legalpaper]
	onecolumn, % Ein- oder zweispaltig [onecolumn, twocolumn]
	final, % Entwurf oder finale Version [draft, final]
	ngerman, % neue deutsche Rechtschreibung
	reqno, % Nummer bei Formeln links statt rechts [leqno, reqno]
	fleqn, % Formeln linksbündig [fleqn]
	twoside, % ein- oder zweiseitig [oneside, twoside]
	openright, % wo Kapitel beginnen [openright, openany]
	parskip=2ex   % half*,
	headings=big,
	listof=totoc,
}{scrbook}

% Default option---pass to scrbook.cls, since that is the base.
\DeclareOption*{%
	\PassOptionsToClass{\CurrentOption}{scrbook}%
}

\ProcessOptions\relax

% Load the base class and required packages.
\LoadClassWithOptions{scrbook}

% ---------------------------------------------------------------------------------

% \RequirePackage{ucs} % incompatible to biblatex
\RequirePackage[utf8]{inputenc}  % use utf8 instead of utf8x 
\RequirePackage[T1]{fontenc}
\RequirePackage[ngerman, english]{babel}
\RequirePackage[babel, german=quotes]{csquotes}

% Translation Helpers
\newcommand{\german}[2][ngerman]{%
  \edef\temp{\string#1}
  \ifx\temp\languagename%
  #2%
  \fi%
}
\newcommand{\english}[2][english]{%
  \edef\temp{\string#1}
  \ifx\temp\languagename%
    #2%
  \fi%
}
\newcommand{\DeEn}[2]{%
    \german{#1}%
    \english{#2}%
}
% \german{Deutscher Text}\enlish{enlish text}
% choose via \selectlanguage


\RequirePackage{lmodern}   % lmodern, times, ...

\RequirePackage{microtype}

% Überprüfen, ob notwendig

\RequirePackage[automark]{scrlayer-scrpage}
\RequirePackage{calc}
\RequirePackage{array}
\RequirePackage{newcent}
\RequirePackage{setspace}  

\RequirePackage{blindtext}  
  
\RequirePackage{placeins}
\RequirePackage{float}
\RequirePackage[final,colorlinks=true,citecolor=blue,linkcolor=black]{hyperref}
% --- Ende der zu überprüfenden Liste
% ----------------------------------------------

% Grafik

\RequirePackage{graphicx}
\RequirePackage{pgf}
%\RequirePackage{caption}[2008/08/24]
\RequirePackage{caption}
\RequirePackage{subcaption}


% Mathe

\RequirePackage{amsmath}
\RequirePackage{amssymb}
\RequirePackage{amstext}
\RequirePackage{amsthm}
\RequirePackage{mathtools}
\RequirePackage{nicefrac}
\RequirePackage{siunitx}

% Algorithmen und Quellcode

\RequirePackage[formats]{listings}
\RequirePackage{algorithm}
\RequirePackage{algpseudocode}
\RequirePackage{struktex}
\RequirePackage{filecontents}
\RequirePackage{forloop}
\RequirePackage{ifthen}
\RequirePackage{cancel}

% Tabellen

\RequirePackage{longtable}
\RequirePackage{tabularx}
\RequirePackage{multirow}
\RequirePackage{multicol}
\RequirePackage{booktabs}

% Ein paar Symbole
\RequirePackage{textcomp}
\RequirePackage{gensymb}
\RequirePackage{newunicodechar}
%\newunicodechar{°}{\degree}
\RequirePackage{marvosym}

% Indizes
\RequirePackage{makeidx}\makeindex
\RequirePackage[withpage, printonlyused]{acronym}

% Literaturverzeichnis
\PassOptionsToPackage{toc=bib}{biblatex}
\usepackage[%
            style=numeric,%
            %style=alphabetic,%
            %style=authoryear,%
            %style=authortitle,%
            %style=verbose,%
            %style=draft,%
            %%
            %autocite=plain,%
            %autocite=inline,%
            %autocite=footnote,%
            %autocite=supercript,%
            backend=biber
            ]{biblatex}
% Verzeichnisse Automatisch ins Inhaltsverzeichnis:
\RequirePackage[chapter]{tocbibind}
%---------------------------------------------------------------------------------

\lstloadlanguages{R,Java,Python,[ISO]C++,[ANSI]C++,[ANSI]C}
\RequirePackage{xcolor}
\definecolor{commentgreen}{RGB}{2,112,10}
\definecolor{eminence}{RGB}{108,48,130}
\definecolor{weborange}{RGB}{255,165,0}
\definecolor{frenchplum}{RGB}{129,20,83}

\lstset{
	inputencoding=utf8,
	extendedchars=\true,
%
	numbers=left,
	frame=tb,
	tabsize=2,
%
	captionpos=b,
	breaklines=true,
	breakatwhitespace=true,
	%prebreak=\raisebox{0ex}[0ex][0ex]{\color{gray}\ensuremath{\rhookswarrow}},
	%postbreak=\raisebox{0ex}[0ex][0ex]{\color{gray}\ensuremath{\rcurvearrowse\space}},
%
	xleftmargin=4ex,
	xrightmargin=0ex,
%
	showtabs=false,
	showspaces=false,
	showstringspaces=false,
%
	basicstyle=\ttfamily\color{black}\small,
	keywordstyle=\color{eminence},
	stringstyle=\color{red},
	commentstyle=\color{commentgreen},
	numberstyle=\color{gray},
	identifierstyle=\color{black},
	emphstyle=\color{blue},
	emph={int,char,double,float,unsigned,void,bool},
	%directivestyle=\ttfamily\color{red},
    keywordstyle=[2]{\color{weborange}},
    otherkeywords={>,<,.,;,-,!,=,~},
    morekeywords=[2]{>,<,.,;,-,!,=,~},
%
	literate={%
		{Ö}{{\"O}}1 
		{Ä}{{\"A}}1 
		{Ü}{{\"U}}1 
		{ß}{{\ss}}2 
		{ü}{{\"u}}1 
		{ä}{{\"a}}1 
		{ö}{{\"o}}1
		}
}

\lstdefinelanguage{R}{% https://stat.ethz.ch/pipermail/r-help/2006-September/113688.html
	morekeywords=[1]{\<<-},%
	sensitive=false,
	morecomment=[l]{\#},
	morecomment=[s]{/*}{*/},
	morestring=[b]",
}[keywords,comments,strings]

\lstdefinelanguage{CSS}{
	morekeywords={color,display},
	sensitive=false,
	morecomment=[l]{//},
	morecomment=[s]{/*}{*/},
	morestring=[b]",
}

\lstdefinelanguage{C}{%%
%	morekeywords={color,display},
	sensitive=false,
	morecomment=[l]{//},
	morecomment=[s]{/*}{*/},
	morestring=[b]"
}


% Error information should be more than the default.
\setcounter{errorcontextlines}{5}

% ---------------------------------------------------------------------------------
% Pagestyle

\pagestyle{scrheadings} 
\clearscrheadfoot
\ihead{\headmark}
\ohead{\pagemark}
\raggedbottom

%\onehalfspacing % Zeilenabstand: 1,5
\setlength\parskip{2ex}

% Kein Einzug bei neuem Absatz
\setlength{\parindent}{0em}

% ---------------------------------------------------------------------------------
% Titel
\newcommand{\Informatik}{\depname{\DeEn{Informatik}%
                                       {Computer Science}}}
\newcommand{\Elektronik}{\depname{\DeEn{Elektronik}%
                                       {Electical Engineering}}}
\newcommand{\DataScience}{\depname{\DeEn{Data Science}%
                                        {Data Science}}}                                       
\def\@depname{}
\def\depname#1{\def\@depname{#1}}


%\def\@doctype{}%
\newif\ifpsb\psbfalse
\def\doctype#1{\def\@doctype{#1}}%

\newcommand{\Praxissemesterbericht}{%
  \doctype{\DeEn{Praxissemesterbericht}%
                {Internship Report}}%
  \psbtrue%
}
\newcommand{\Projektbericht}{%
  \doctype{\DeEn{Projektbericht}%
                {Project Report}}%
  \psbfalse%
}
\newcommand{\Bachelorarbeit}{%
  \doctype{\DeEn{Bachelorarbeit}%
                {Bachelor's Thesis}}%
  \psbfalse%
}
\newcommand{\Seminararbeit}{%
  \doctype{\DeEn{Seminararbeit}%
                {Seminar Paper}}%
  \psbfalse%
}
\newcommand{\Masterarbeit}{%
  \doctype{\DeEn{Masterarbeit}%
                {Master's Thesis}}%
  \psbfalse%
}

\newif\ifexaminerIsAProfessor\examinerIsAProfessortrue
%\def\@examinerA{}
\def\examinerA#1{\def\@examinerA{#1}}%

%\def\@examinerB{}
\def\examinerB#1{\def\@examinerB{#1}}%

\def\AbgabeDatumTok{\@empty}

%\def\@matrikelnr{}
\def\matrikelnr#1{\def\@matrikelnr{#1}}%

%\def\@companyname{}
\def\companyname#1{\def\@companyname{#1}}%

\renewcommand\maketitle{\begin{titlepage}%
	\sffamily
	\begin{flushright}
		\DeEn{%
		  \includegraphics[width=.75\textwidth]{img/htw-aalen.pdf}%
		}{%
		  \includegraphics[width=.75\textwidth]{img/htw-aalen-en.pdf}%
		}
	\end{flushright}
	\vskip 2cm
	\begin{flushleft}
		\par \large \color{gray}
		\ifx\@doctype\undefined%
%
		\else%
		\@doctype\\%
		\DeEn{Studiengang}%
		     {Course of Studies}:\xspace\@depname\xspace\\[0ex]
		\fi%
		\par \rule{\textwidth}{0.25pt}

	\end{flushleft}
%
	\bigskip
	\bigskip
	\bigskip
	\begin{center}
		\ifx\@title\undefined%
		%
		\else
		\par\Huge\textbf{\@title}\bigskip%
		\fi%
		\ifx\@companyname\undefined%
%
		\else%
		\par \large \color{black}%
		\DeEn{bei}%
		     {at} \par%
		\Large\@companyname\bigskip%
		\fi%	
		\ifx\@author\undefined%
%
		\else%
		\par \large \color{black}%
		\DeEn{von}%
		     {by} \par%		
		\Large\@author%
		\fi%
		\ifx\@matrikelnr\undefined%
%
        \else%
        \par\Large \color{gray}%
        \@matrikelnr%
        \fi%
  	\end{center}
	\vfill
%
%
	\begin{tabular}{ll}
		\ifx\@examinerA\undefined
		\else
		\ifexaminerIsAProfessor
		\DeEn{Betreuender}%
		     {Supervising} Professor:		& \@examinerA \\
		\else
		\DeEn{Betreuender Mitarbeiter}%
		     {Supervising Faculty Staff}:	& \@examinerA \\
		\fi
		\fi
		\ifx\@examinerB\undefined
		\else
		\DeEn{Zweitprüfer}%
		     {Co-Supervisor}:				& \@examinerB \\
		\fi
		\ifx\@date\undefined
		\else
		& \\
		\DeEn{Einreichungsdatum}%
		     {Submission Date}:			& \@date \\
		\fi
	\end{tabular}
\end{titlepage}
}

% ---------------------------------------------------------------------------------
% Praxisstelle / Eidesstattliche Versicherung


%\def\@industrialsector{}
\def\industrialsector#1{\def\@industrialsector{#1}}%

%\def\@department{}
\def\department#1{\def\@department{#1}}%

%\def\@companystreet{}
\def\companystreet#1{\def\@companystreet{#1}}%

%\def\@companycity{}
\def\companycity#1{\def\@companycity{#1}}%

%\def\@advisorname{}
\def\advisorname#1{\def\@advisorname{#1}}%

%\def\@advisorphone{}
\def\advisorphone#1{\def\@advisorphone{#1}}%

%\def\@advisoremail{}
\def\advisoremail#1{\def\@advisoremail{#1}}%

\def\makeworkplace{%

\chapter*{\DeEn{Angaben zur Firma}%
               {Information about the Company}}
\DeEn{\addcontentsline{toc}{chapter}{Angaben zur Firma}}%
     {\addcontentsline{toc}{chapter}{Information about the Company}}
	\begin{tabular}{ll}
		\ifx\@companyname\undefined
		\else
		\textbf{\DeEn{Unternehmen}%
		             {Company}:}			& \@companyname \\
		\fi
		\ifx\@industrialsector\undefined
		\else
		\textbf{\DeEn{Branche}%
		             {Industrial Sector}:}	& \@industrialsector \\
		\fi
		\ifx\@department\undefined
		\else
		\textbf{\DeEn{Abteilung}%
		             {Department}:}			& \@department \\
		\fi
		\ifx\@companystreet\undefined
		\else
		\textbf{\DeEn{Adresse}%
		             {Address}:}			& \@companystreet \\
		\fi
		\ifx\@companycity\undefined
		\else
											& \@companycity \\
		\fi
		 									& \\
		\ifx\@advisorname\undefined
		\else
		\textbf{\DeEn{Betreuer}%
		             {Supervisor}:}			& \@advisorname \\
		\fi
		\ifx\@advisorphone\undefined
		\else
		\textbf{\DeEn{Telefon}%
		             {Telephone}:}			& \@advisorphone \\
		\fi
		\ifx\@advisoremail\undefined
		\else
		\textbf{\DeEn{E-Mail}%
		             {E-Mail}:}				& \@advisoremail \\
		\fi
	\end{tabular}%
}

\def\makeaffirmation{%
\chapter*{\DeEn{Eidesstattliche Erkl\"arung}%
               {Statutory Declaration}}
\DeEn{\addcontentsline{toc}{chapter}{Eidesstattliche Erkl\"arung}}%
     {\addcontentsline{toc}{chapter}{Statutory Declaration}}

\DeEn{%
  Hiermit erkl\"are ich, \textbf{\@author}, dass ich die vorliegenden Angaben
  in dieser Arbeit%
}{%
  I, \textbf{\@author}, hereby declare that I have wrote the information
  available in this work%
}
\ifx\@companyname\undefined
\else
\DeEn{bei}{at} \textbf{\@companyname}%
\fi
\DeEn{wahrheitsgetreu und selbständig verfasst habe.}%
     {truthfully and independently by myself.}

\DeEn{%
  Weiterhin versichere ich, keine anderen als die angegebenen Quellen und
  Hilfsmittel benutzt zu haben, dass alle Ausführungen, die anderen 
  Schriften w\"ortlich oder sinngem\"a\ss{} entnommen wurden, kenntlich 
  gemacht sind und dass die Arbeit in gleicher oder \"ahnlicher Fassung 
  noch nicht Bestandteil einer Studien- oder Prüfungsleistung war.%
}{%
  Furthermore, I assure that I have used no other than the specified
  sources and aids, that I have marked all quotations that I have used from
  other sources, and that the work in the same or similar was not yet part of a
  study or examination.%
}
\vspace{4em}

\DeEn{\makebox[\textwidth/2]{Ort, Datum} Unterschrift (Student)}%
     {\makebox[\textwidth/2]{Location, Date} Signature (Student)}
\ifx\@companyname\undefined
\else
\ifx\@advisorname\undefined
\else
\ifpsb
\section*{\DeEn{Best\"atigung der inhaltlichen Richtigkeit}%
               {Confirmation of the correctness of the content}}
\DeEn{%
  Der vorliegende Bericht wurde durch den zust\"andigen Betreuer
  \textbf{\@advisorname} Korrektur gelesen und auf inhaltliche
  Korrektheit gepr\"uft.%
}{%
  The report had been proof read and the correctness of the content
  has been approved by my supervisor \textbf{\@advisorname}.%
}

\vspace{4em}
\DeEn{\makebox[\textwidth/2]{Ort, Datum} Unterschrift (Betreuer)}%
     {\makebox[\textwidth/2]{Location, Date} Signature (Supervisor)}
\fi
\fi
\fi
}

%-----------------------------------------------------------------------------
\newcommand{\listoflistings}{%
  \lstlistoflistings
  \DeEn{%
    \renewcommand{\lstlistingname}{Quelltext}%
    \renewcommand{\lstlistlistingname}{Quelltextverzeichnis}%
    \addcontentsline{toc}{chapter}{Quelltextverzeichnis}%
  }{%
    \renewcommand{\lstlistlistingname}{List of Listings}%
    \addcontentsline{toc}{chapter}{List of Listings}%
  }
}

\newcommand{\listofabbreviations}{%
  \chapter*{\DeEn{Abkürzungsverzeichnis}%
                 {List of Abbreviations}}%
  \DeEn{\addcontentsline{toc}{chapter}{Abkürzungsverzeichnis}}%
       {\addcontentsline{toc}{chapter}{List of Abbreviations}}%
}

\newenvironment{abstract}{%
  \chapter*{\DeEn{Kurzfassung}%
           {Abstract}}
  \DeEn{\addcontentsline{toc}{chapter}{Kurzfassung}}%
       {\addcontentsline{toc}{chapter}{Abstract}}
}{}