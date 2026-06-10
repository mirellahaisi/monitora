(function () {
  "use strict";

  const STORAGE_KEY = "monitoraIdioma";
  const LEGACY_KEYS = ["monitora.lang", "idioma", "lang"];
  const DEFAULT_LANGUAGE = "pt";
  const SUPPORTED_LANGUAGES = {
    pt: { label: "PT", name: "Português", locale: "pt-BR", htmlLang: "pt-BR" },
    en: { label: "EN", name: "English", locale: "en-US", htmlLang: "en-US" },
    es: { label: "ES", name: "Español", locale: "es-ES", htmlLang: "es-ES" }
  };

  const textOriginals = new WeakMap();
  const textLastTranslated = new WeakMap();
  const attrOriginals = new WeakMap();
  const attrLastTranslated = new WeakMap();
  let currentLanguage = readLanguage();
  let observer = null;
  let translating = false;
  let originalTitle = document.title || "";

  const TEXT = {
    en: {
      "acessar com suas credenciais institucionais": "Sign in with your institutional credentials",
      "acessar o sistema": "Access the system",
      "acessar o sistema ->": "Access the system ->",
      "acessar sistema ->": "Access system ->",
      "acompanhe seu": "Track your",
      "academico": "academic",
      "academica": "academic",
      "acesso por perfil": "Role-based access",
      "acesso seguro": "Secure access",
      "acoes": "Actions",
      "a acao nao pode ser desfeita": "This action cannot be undone",
      "a especialidade deve ter no minimo 3 caracteres.": "The specialty must be at least 3 characters long.",
      "a idade minima permitida e de 12 anos.": "The minimum allowed age is 12.",
      "a nova senha deve ter pelo menos 6 caracteres.": "The new password must be at least 6 characters long.",
      "0,00": "0.00",
      "a senha inicial usa a data de nascimento no formato ddmmaa.": "The initial password uses the birth date in DDMMYY format.",
      "a senha inicial usa a data de nascimento no formato DDMMAA.": "The initial password uses the birth date in DDMMYY format.",
      "a data e hora de fim deve ter pelo menos 1 hora de diferenca do inicio.": "The end date and time must be at least 1 hour after the start.",
      "a data e hora de fim nao podem estar no passado.": "The end date and time cannot be in the past.",
      "a data e hora de inicio nao podem estar no passado.": "The start date and time cannot be in the past.",
      "abrir detalhes": "Open details",
      "abril": "April",
      "agosto": "August",
      "altere pelo menos um campo antes de salvar.": "Change at least one field before saving.",
      "aluno": "Student",
      "aluno(a)": "Student",
      "alunos": "Students",
      "alunos devem ter mais de 12 anos.": "Students must be older than 12.",
      "alunos matriculados": "Enrolled students",
      "apenas alunos": "Students only",
      "apenas professores": "Teachers only",
      "aprovados": "Passed",
      "ativas": "active",
      "ativar modo escuro": "Enable dark mode",
      "atencao": "Attention",
      "atribuido": "Assigned",
      "atribuir professor": "Assign teacher",
      "aulas": "Classes",
      "buscar": "Search",
      "bem-vindo,": "Welcome,",
      "calendario": "Calendar",
      "cancelar": "Cancel",
      "capacidade": "Capacity",
      "carregando...": "Loading...",
      "carregando notas...": "Loading grades...",
      "codigo": "Code",
      "codigo:": "Code:",
      "com precisao": "with precision",
      "confirmar": "Confirm",
      "coordenacao": "Coordination",
      "cor": "Color",
      "corrija as notas abaixo antes de continuar:": "Fix the grades below before continuing:",
      "cpf": "CPF",
      "curso": "Course",
      "cursos": "Courses",
      "cadastrados": "registered",
      "cadastre e gerencie alunos, professores e coordenadores com controle de acesso por papel.": "Register and manage students, teachers, and coordinators with role-based access control.",
      "cada usuario ve apenas o que e relevante para seu papel - coordenador, professor ou aluno.": "Each user sees only what matters to their role - coordinator, teacher, or student.",
      "cada usuario ve apenas o que e relevante para seu papel — coordenador, professor ou aluno.": "Each user sees only what matters to their role - coordinator, teacher, or student.",
      "comunicados": "Announcements",
      "data": "Date",
      "data / hora inicio *": "Start date / time *",
      "data de nascimento": "Birth date",
      "dados pessoais": "Personal data",
      "de presenca nas aulas": "attendance in classes",
      "desenvolvedora": "Developer",
      "desenvolvedor": "Developer",
      "deve ter pelo menos 1 hora de diferenca do inicio": "must be at least 1 hour after the start",
      "dezembro": "December",
      "desempenho": "Performance",
      "desempenho e": "performance and",
      "desativar modo escuro": "Disable dark mode",
      "descrição": "Description",
      "detalhes opcionais...": "Optional details...",
      "digite sua senha atual": "Enter your current password",
      "digite sua senha atual para continuar.": "Enter your current password to continue.",
      "disciplinas": "subjects",
      "e-mail": "Email",
      "edicao": "Editing",
      "editar": "Edit",
      "editar curso": "Edit Course",
      "editar dados da turma": "Edit class data",
      "editar perfil": "Edit profile",
      "em alerta": "in alert",
      "em atencao": "Needs attention",
      "enviar": "Send",
      "entrar na plataforma": "Enter platform",
      "entrega": "Assignment",
      "equipe": "Team",
      "erro": "Error",
      "erro ao buscar cursos.": "Error fetching courses.",
      "erro ao carregar dados do usuario.": "Error loading user data.",
      "erro ao carregar eventos.": "Error loading events.",
      "erro ao carregar notas.": "Error loading grades.",
      "erro ao carregar professores.": "Error loading teachers.",
      "erro ao carregar suas notas.": "Error loading your grades.",
      "evolua": "grow",
      "escolha": "Choose",
      "escolher mes/ano": "choose month/year",
      "esqueceu a sua senha?": "Forgot your password?",
      "especialidade": "Specialty",
      "evento pessoal (visivel so para mim)": "Personal event (visible only to me)",
      "ex.: analise e desenvolvimento de sistemas": "Ex.: Systems Analysis and Development",
      "ex.: matematica": "Ex.: Mathematics",
      "ex.: prova de poo": "Ex.: OOP exam",
      "ex.: joao da silva": "Ex.: John Smith",
      "excluir": "Delete",
      "excluir curso": "Delete course",
      "exporte relatorios de frequencia individuais por aluno, materia e periodo com um clique.": "Export individual attendance reports by student, subject, and period with one click.",
      "falha ao buscar cursos.": "Failed to fetch courses.",
      "falha ao buscar materias.": "Failed to fetch subjects.",
      "falha ao buscar notas.": "Failed to fetch grades.",
      "falha ao buscar professores.": "Failed to fetch teachers.",
      "falha ao conectar com o servidor.": "Failed to connect to the server.",
      "falha ao salvar": "Failed to save",
      "falha na conexao": "Connection failed",
      "falha na conexao.": "Connection failed.",
      "fazer login": "Log in",
      "fechar": "Close",
      "fevereiro": "February",
      "filtro": "Filter",
      "filtre suas materias e acompanhe da menor para a maior frequencia": "Filter your subjects and track attendance from lowest to highest",
      "filtrar matriculados...": "Filter enrolled students...",
      "faltam": "Missing",
      "faltas": "Absences",
      "formatar": "Format",
      "frequencia": "Attendance",
      "frequencia geral dentro do esperado.": "Overall attendance is within expectations.",
      "frequencia geral institucional.": "Institution-wide average attendance.",
      "frequencia maior para menor": "Attendance high to low",
      "frequencia menor para maior": "Attendance low to high",
      "frequencia regular": "Regular attendance",
      "frequencias e notas sempre atualizadas": "Attendance and grades always up to date",
      "frequencias, notas e comunicados reunidos em uma plataforma moderna para alunos, professores e coordenadores.": "Attendance, grades, and announcements brought together in a modern platform for students, teachers, and coordinators.",
      "funcionalidades": "Features",
      "ferramentas projetadas para simplificar a gestao academica do inicio ao fim.": "Tools designed to simplify academic management from start to finish.",
      "gerencie alunos, professores e coordenadores": "Manage students, teachers, and coordinators",
      "gerencie turmas": "Manage classes",
      "gestao completa de turmas, professores, alunos e desempenho academico": "Complete management of classes, teachers, students, and academic performance",
      "gestao de usuarios": "User Management",
      "hoje": "Today",
      "idioma": "Language",
      "idade invalida": "Invalid age",
      "inicio": "Home",
      "informe a data de nascimento.": "Enter the birth date.",
      "informe o cpf.": "Enter the CPF.",
      "informe um cpf valido.": "Enter a valid CPF.",
      "informe um e-mail valido.": "Enter a valid email address.",
      "informe um salario valido no formato 0,00.": "Enter a valid salary in 0.00 format.",
      "informe um telefone valido com ddd.": "Enter a valid phone number with area code.",
      "inteligencia": "intelligence",
      "janeiro": "January",
      "julho": "July",
      "junho": "June",
      "lancar notas": "Enter grades",
      "leciona": "teaches",
      "limpar": "Clear",
      "login": "Login",
      "marco": "March",
      "materia": "Subject",
      "materia em ordem alfabetica": "Subject in alphabetical order",
      "materias": "Subjects",
      "matriculados": "enrolled",
      "maio": "May",
      "media": "Average",
      "media da turma": "Class average",
      "media geral da turma": "Class overall average",
      "media geral das disciplinas": "Overall subject average",
      "media geral instituicao": "Institution overall average",
      "monitore o": "Monitor",
      "mensagens": "Messages",
      "mensagens e comunicados": "Messages and announcements",
      "mensagens recentes": "Recent messages",
      "minha frequencia": "My Attendance",
      "minha turma": "My Class",
      "minimizar menu": "Minimize menu",
      "monitore o desempenho academico com precisao": "Monitor academic performance with precision",
      "mostrando": "Showing",
      "nascimento": "Birth date",
      "nenhum aluno encontrado para essa selecao.": "No student found for this selection.",
      "nenhum aluno matriculado.": "No enrolled student.",
      "nenhuma informacao foi alterada.": "No information was changed.",
      "nenhuma materia encontrada": "No subject found",
      "nenhuma materia vinculada.": "No linked subject.",
      "nenhuma mensagem.": "No message.",
      "nenhum resultado encontrado": "No result found",
      "nome": "Name",
      "nome completo": "Full name",
      "notas": "Grades",
      "nova senha": "New password",
      "o ano e sempre o corrente e nao pode ser alterado": "The year is always the current one and cannot be changed",
      "o monitora+ centraliza frequencias, notas e mensagens em uma plataforma intuitiva para professores, coordenadores e alunos.": "Monitora+ centralizes attendance, grades, and messages in an intuitive platform for teachers, coordinators, and students.",
      "o nome deve ter no minimo 3 caracteres.": "The name must be at least 3 characters long.",
      "outubro": "October",
      "pagina inicial": "Home",
      "painel de gestao": "Management dashboard",
      "periodo": "Period",
      "perfil": "Profile",
      "perfis de acesso - aluno, professor e coordenacao": "Access profiles - student, teacher, and coordination",
      "perfis de acesso — aluno, professor e coordenacao": "Access profiles - student, teacher, and coordination",
      "pesquisar": "Search",
      "pesquisar materia": "Search subject",
      "pesquise o aluno": "Search student",
      "pesquise o curso": "Search course",
      "pesquise o professor": "Search teacher",
      "pesquise a materia": "Search subject",
      "pesquise a turma": "Search class",
      "plataforma academica": "Academic Platform",
      "preencha apenas se quiser alterar a senha": "Fill in only if you want to change the password",
      "preencha e-mail, senha atual e nova senha.": "Fill in email, current password, and new password.",
      "presenca": "Attendance",
      "pronto para comecar?": "Ready to start?",
      "projeto desenvolvido por estudantes comprometidos com a inovacao na educacao.": "Project developed by students committed to innovation in education.",
      "professor": "Teacher",
      "professor nao informado": "Teacher not provided",
      "professores": "Teachers",
      "professores e coordenadores devem ter mais de 18 anos.": "Teachers and coordinators must be older than 18.",
      "prova": "Exam",
      "publique mensagens vinculadas as materias para que alunos sejam notificados diretamente em suas turmas.": "Publish messages linked to subjects so students are notified directly in their classes.",
      "qua": "WED",
      "rascunho salvo": "Draft saved",
      "real-time": "Real-time",
      "registre presencas e faltas por materia e turma, com visualizacao grafica do percentual de frequencia.": "Record attendance and absences by subject and class, with a chart view of attendance percentage.",
      "relatorios para download": "Downloadable reports",
      "remover": "Remove",
      "remover professor": "Remove teacher",
      "sair": "Sign out",
      "salario": "Salary",
      "salario (r$)": "Salary (R$)",
      "salvar": "Save",
      "salvar alteracoes": "Save changes",
      "seguranca": "Security",
      "selecione": "Select",
      "selecione a materia": "Select the subject",
      "selecione a turma": "Select the class",
      "selecione professor, turma e materia para visualizar as notas.": "Select teacher, class, and subject to view grades.",
      "selecione um curso": "Select a course",
      "selecione o aluno": "Select the student",
      "selecione o curso": "Select the course",
      "selecione o professor": "Select the teacher",
      "selecione uma turma": "Select a class",
      "sem alertas disponiveis.": "No alerts available.",
      "sem dados": "No data",
      "sem notas": "No grades",
      "senha": "Password",
      "sessao protegida": "Protected session",
      "sua senha": "Your password",
      "suas notas, frequencia e agenda reunidos num so painel": "Your grades, attendance, and agenda together in one dashboard",
      "sistema de monitoramento academico": "Academic Monitoring System",
      "tudo que voce precisa em um so lugar": "Everything you need in one place",
      "sucesso": "Success",
      "telefone": "Phone",
      "titulo *": "Title *",
      "todos": "All",
      "todos (alunos e professores)": "All (students and teachers)",
      "todos os direitos reservados": "All rights reserved",
      "todas as materias": "All subjects",
      "total": "total",
      "total de aulas": "Total classes",
      "turma": "Class",
      "turmas ativas": "Active classes",
      "turmas em que voce leciona": "Classes you teach",
      "turmas": "Classes",
      "use:": "Use:",
      "usuario": "User",
      "usuarios": "Users",
      "ver funcionalidades": "View features",
      "ver todas": "View all",
      "ver turmas": "View classes",
      "visao geral da instituicao": "Institution overview",
      "visao geral de todas as turmas ativas": "Overview of all active classes",
      "visualizar": "View",
      "visivel para": "Visible to",
      "carregando sua frequencia...": "Loading your attendance...",
      "digite a nova senha": "Enter the new password",
      "frequencia do aluno": "Student Attendance",
      "frequencia insuficiente - abaixo do minimo exigido (75%)": "Insufficient attendance - below the required minimum (75%)",
      "frequencia regular - acima do minimo exigido (75%)": "Regular attendance - above the required minimum (75%)",
      "nao foi possivel carregar sua frequencia. tente novamente.": "Unable to load your attendance. Please try again.",
      "selecione a materia, turma e aluno para visualizar a frequencia": "Select subject, class, and student to view attendance",
      "selecione curso, materia, turma e aluno para visualizar a frequencia": "Select course, subject, class, and student to view attendance",
      "1o semestre": "1st semester",
      "2o semestre": "2nd semester",
      "a 100": "to 100",
      "abaixo do minimo exigido de 75%": "Below the required minimum of 75%",
      "acesso negado": "Access denied",
      "agenda da semana": "Weekly Agenda",
      "alertas": "Alerts",
      "alertas de frequencia": "Attendance alerts",
      "alternar tema": "Toggle theme",
      "aluno:": "Student:",
      "alunos abaixo de 75%": "Students below 75%",
      "alunos sob responsabilidade": "Students in your care",
      "ano": "Year",
      "aprovado em": "Passed in",
      "as notas serao registradas e ficarao visiveis para os alunos.": "The grades will be registered and become visible to students.",
      "atencao a frequencia": "Attendance warning",
      "ativa": "Active",
      "ativo": "Active",
      "aula": "Class",
      "ausente": "Absent",
      "aviso": "Notice",
      "ainda nao ha medias calculadas.": "No averages calculated yet.",
      "buscar por nome ou codigo...": "Search by name or code...",
      "cadastre, edite e gerencie as disciplinas da instituicao": "Register, edit, and manage institution subjects",
      "cadastre, edite e gerencie os cursos disponiveis na instituicao": "Register, edit, and manage available courses",
      "carga horaria": "Course load",
      "carga horaria (h)": "Course load (h)",
      "carregando alunos...": "Loading students...",
      "carregando cursos...": "Loading courses...",
      "carregando materias...": "Loading subjects...",
      "carregando mensagens...": "Loading messages...",
      "carregando suas turmas...": "Loading your classes...",
      "carregando turmas...": "Loading classes...",
      "chamada incompleta": "Incomplete attendance",
      "colegas de turma": "Classmates",
      "coordenador": "Coordinator",
      "criar turma": "Create class",
      "curso atualizado!": "Course updated!",
      "curso cadastrado!": "Course registered!",
      "curso removido.": "Course removed.",
      "data / hora": "Date / time",
      "data / hora fim": "End date / time",
      "data / hora inicio": "Start date / time",
      "data da aula": "Class date",
      "descricao": "Description",
      "descricao (opcional)": "Description (optional)",
      "desempenho medio por turma": "Average performance by class",
      "desempenho por turma": "Performance by class",
      "detalhe do evento": "Event details",
      "disciplinas cursando": "Enrolled subjects",
      "distribuicao de usuarios": "User distribution",
      "dom": "Sun",
      "editar turma": "Edit class",
      "enviado!": "Sent!",
      "enviados": "Sent",
      "enviar mensagem": "Send message",
      "erro ao carregar cursos.": "Error loading courses.",
      "erro ao salvar presenca.": "Error saving attendance.",
      "esta area e exclusiva para coordenadores.": "This area is exclusive to coordinators.",
      "evento": "Event",
      "evento criado!": "Event created!",
      "excluida!": "Deleted!",
      "excluido!": "Deleted!",
      "excluir curso?": "Delete course?",
      "excluir materia?": "Delete subject?",
      "expandir menu": "Expand menu",
      "falha de conexao. tente novamente.": "Connection failure. Try again.",
      "falha de conexao ao carregar cursos.": "Connection failure loading courses.",
      "falha de conexao ao carregar materias.": "Connection failure loading subjects.",
      "faltando:": "Missing:",
      "formato invalido": "Invalid format",
      "frequencia critica": "Critical attendance",
      "frequencia geral": "Overall attendance",
      "frequencia media institucional.": "Institutional average attendance.",
      "frequencia:": "Attendance:",
      "gerencie alunos, materias e professores": "Manage students, subjects, and teachers",
      "gerencie turmas e acompanhe o progresso": "Manage classes and track progress",
      "gerir": "Manage",
      "gerir turma": "Manage class",
      "gestao de cursos": "Course Management",
      "gestao de materias": "Subject Management",
      "inativa": "Inactive",
      "inativo": "Inactive",
      "informe a carga horaria.": "Enter the course load.",
      "informe o codigo.": "Enter the code.",
      "informe o nome da materia.": "Enter the subject name.",
      "informe o nome do curso.": "Enter the course name.",
      "informe o prefixo.": "Enter the prefix.",
      "informe uma carga horaria valida (min. 1h).": "Enter a valid course load (min. 1h).",
      "lancamento de notas": "Grade entry",
      "leram": "read",
      "mais": "more",
      "manha": "Morning",
      "marque presenca ou ausencia para todos os alunos antes de salvar.": "Mark present or absent for all students before saving.",
      "materia atualizada!": "Subject updated!",
      "materia cadastrada!": "Subject registered!",
      "materia removida.": "Subject removed.",
      "materia:": "Subject:",
      "media geral": "Overall average",
      "mensagem": "Message",
      "mes anterior": "Previous month",
      "minhas materias": "My subjects",
      "minhas notas": "My grades",
      "nenhum alerta no momento.": "No alerts at the moment.",
      "nenhum aluno em alerta.": "No students on alert.",
      "nenhum dado foi alterado.": "No data was changed.",
      "nenhuma alteracao": "No changes",
      "nenhuma materia atribuida.": "No subjects assigned.",
      "nenhuma materia encontrada para sua turma.": "No subjects found for your class.",
      "nenhuma mensagem recente.": "No recent messages.",
      "nenhuma opcao disponivel": "No options available",
      "nenhuma turma.": "No classes.",
      "nenhuma turma encontrada com esses filtros.": "No classes found with these filters.",
      "nenhum curso cadastrado ainda.": "No courses registered yet.",
      "nenhum curso encontrado para a busca.": "No courses found.",
      "nenhuma materia cadastrada ainda.": "No subjects registered yet.",
      "nenhuma materia encontrada para a busca.": "No subjects found.",
      "noite": "Evening",
      "nome da materia": "Subject name",
      "nome do curso": "Course name",
      "nota 1": "Grade 1",
      "nota 2": "Grade 2",
      "notas, frequencias e alertas das suas turmas em tempo real": "Grades, attendance, and alerts for your classes in real-time",
      "notas ainda nao lancadas pelo professor.": "Grades not yet submitted by the teacher.",
      "notas incompletas": "Incomplete grades",
      "notas por materia": "Grades by subject",
      "notas por turma": "Grades by class",
      "notas publicadas!": "Grades published!",
      "nova materia": "New subject",
      "nova mensagem": "New message",
      "nova turma": "New class",
      "novo curso": "New course",
      "o codigo deve ter pelo menos 2 caracteres.": "The code must have at least 2 characters.",
      "o nome deve ter pelo menos 3 caracteres.": "The name must have at least 3 characters.",
      "o prefixo deve ter pelo menos 2 caracteres.": "The prefix must have at least 2 characters.",
      "para quem": "To",
      "periodo:": "Period:",
      "prefixo / codigo": "Prefix / Code",
      "prefixo / sigla": "Prefix / Abbreviation",
      "presente": "Present",
      "previa gerada automaticamente": "Preview generated automatically",
      "proximo mes": "Next month",
      "publicar notas": "Publish grades",
      "publicar notas?": "Publish grades?",
      "quem desenvolveu o monitora+": "Who developed Monitora+",
      "qui": "Thu",
      "recebidos": "Received",
      "relatorio de frequencia": "Attendance Report",
      "responsavel": "Responsible",
      "sab": "Sat",
      "salvar chamada": "Save attendance",
      "salvar rascunho": "Save draft",
      "salvando...": "Saving...",
      "seg": "Mon",
      "selecione a turma primeiro": "Select the class first",
      "selecione apenas dias uteis (segunda a sexta).": "Select only business days (Monday to Friday).",
      "selecione curso, materia e turma para registrar as notas": "Select course, subject, and class to register grades",
      "selecione curso, materia, turma e data para carregar os alunos.": "Select course, subject, class, and date to load students.",
      "selecione curso, materia, turma e data para registrar a chamada": "Select course, subject, class, and date to record attendance",
      "selecione curso, professor, turma e materia para visualizar as notas": "Select course, teacher, class, and subject to view grades",
      "selecione o professor primeiro": "Select the teacher first",
      "selecione os dados - nome e codigo serao gerados automaticamente": "Select the data — name and code will be generated automatically",
      "selecione os dados — nome e codigo serao gerados automaticamente": "Select the data — name and code will be generated automatically",
      "selecione um curso, uma materia e uma turma para carregar os alunos.": "Select a course, subject, and class to load students.",
      "sem dados.": "No data.",
      "sem descricao": "No description",
      "sera removida permanentemente.": "will be permanently removed.",
      "sera removido permanentemente.": "will be permanently removed.",
      "sex": "Fri",
      "sim, publicar": "Yes, publish",
      "situacoes que precisam de atencao": "Situations requiring attention",
      "sua turma e colegas matriculados": "Your class and enrolled classmates",
      "suas notas e medias por materia": "Your grades and averages by subject",
      "tarde": "Afternoon",
      "ter": "Tue",
      "tipo": "Type",
      "titulo": "Title",
      "todos os cursos": "All courses",
      "todos os periodos": "All periods",
      "todos os turnos": "All shifts",
      "total de aulas:": "Total classes:",
      "turma / periodo": "Class / Period",
      "turno": "Shift",
      "ver detalhes": "View details",
      "© 2026 · todos os direitos reservados": "© 2026 · All rights reserved",
      "voltar ao inicio": "Back to home",
      "adicionar evento": "Add event",
      "adicionar usuario": "Add user",
      "aprovado": "Approved",
      "a mensagem deve ter mais de 3 caracteres": "The message must be longer than 3 characters",
      "carregando cursos": "Loading courses...",
      "carregando materias": "Loading subjects...",
      "carregando turmas": "Loading classes...",
      "chamada": "Roll call",
      "codigo do curso": "Course code",
      "confira os dados antes de confirmar o envio": "Check the details before confirming",
      "data de fim": "End date",
      "data de inicio": "Start date",
      "descricao do curso": "Course description",
      "deseja enviar a mensagem": "Send message?",
      "editar materia": "Edit subject",
      "erro ao carregar mensagens": "Error loading messages",
      "erro ao carregar turmas": "Error loading classes",
      "escreva a mensagem": "Write the message",
      "excluir materia": "Delete subject",
      "falha na conexao com o servidor": "Connection to server failed",
      "gerencie alunos materias e professores": "Manage students, subjects, and teachers",
      "gerar relatorio": "Generate report",
      "historico de frequencia": "Attendance history",
      "nenhuma mensagem enviada": "No messages sent",
      "nenhuma mensagem recebida": "No messages received",
      "notas publicadas": "Grades published",
      "o titulo deve ter mais de 3 caracteres": "The title must be longer than 3 characters",
      "papel": "Role",
      "preencha o titulo": "Fill in the title",
      "registro de presenca": "Attendance record",
      "reprovado": "Failed",
      "reprovados": "Failed",
      "selecione o coordenador": "Select the coordinator",
      "selecione para quem enviar": "Select who to send to",
      "sem cursos cadastrados": "No courses registered",
      "sem materias cadastradas": "No subjects registered",
      "situacao": "Status",
      "titulo do evento": "Event title",
      "tipo de evento": "Event type",
      "voce": "you",
      "carregando": "Loading...",
      "carregando dados": "Loading data...",
      "erro ao carregar cursos": "Error loading courses",
      "erro ao carregar materias": "Error loading subjects",
      "excluido": "Deleted!",
      "falha de conexao": "Connection failed",
      "falha de conexao tente novamente": "Connection failed. Try again.",
      "materia removida": "Subject removed",
      "nenhum curso cadastrado ainda": "No courses registered yet",
      "nenhum curso encontrado para a busca": "No courses found for your search",
      "nenhum dado foi alterado": "No data was changed",
      "nenhum resultado": "No results",
      "nenhuma materia cadastrada ainda": "No subjects registered yet",
      "nota lancada com sucesso": "Grade entered successfully",
      "nota atualizada com sucesso": "Grade updated successfully",
      "nota atualizada": "Grade updated",
      "nenhuma alteracao detectada": "No changes detected",
      "salvando": "Saving...",
      "salvo": "Saved",
      "curso removido": "Course removed",
      "esta area e exclusiva para coordenadores": "This area is exclusive to coordinators",
      "sim excluir": "Yes, delete",
      "sim salvar": "Yes, save",
      "sim enviar": "Yes, send",
      "nenhum aluno matriculado": "No students enrolled",
      "nenhuma materia vinculada": "No subjects linked",
      "erro ao carregar dados": "Error loading data",
      "sem professor": "No teacher",
      "professor(es)": "Teacher(s)",
      "nenhuma turma encontrada com esses filtros": "No classes found with these filters",
      "alunos matriculados · materias e professores": "Enrolled students · Subjects and teachers",
      "carregando alunos": "Loading students...",
      "selecionar turma": "Select class",
      "selecionar materia": "Select subject",
      "nenhum aluno encontrado": "No students found",
      "tipo aula": "Class type",
      "marcar todos presentes": "Mark all present",
      "marcar todos ausentes": "Mark all absent",
      "buscar usuario": "Search user",
      "filtrar por papel": "Filter by role",
      "nenhum usuario encontrado": "No users found",
      "todos os papeis": "All roles",
      "excluir turma?": "Delete class?",
      "pesquise e selecione um aluno da lista.": "Search and select a student from the list.",
      "pesquise e selecione uma materia da lista.": "Search and select a subject from the list.",
      "pesquise e selecione um professor da lista.": "Search and select a teacher from the list.",
      "sera desvinculado dessa turma.": "will be removed from this class.",
      "deseja desmatricular": "Deregister student?",
      "desvincular": "Unlink",
      "professor removido": "Teacher removed",
      "turma criada": "Class created",
      "turma atualizada": "Class updated",
      "turma criada com sucesso!": "Class created successfully!",
      "turma atualizada com sucesso!": "Class updated successfully!",
      "turma editada com sucesso!": "Class updated successfully!",
      "prefixo invalido.": "Invalid prefix.",
      "nome do curso invalido.": "Invalid course name.",
      "a turma sera desativada esta acao nao pode ser desfeita.": "The class will be deactivated. This cannot be undone.",
      "selecione curso professor turma e materia para visualizar as notas": "Select course, teacher, class, and subject to view grades",
      "selecione curso materia e turma para registrar as notas": "Select course, subject, and class to enter grades",
      "carregando notas": "Loading grades...",
      "erro ao carregar notas": "Error loading grades",
      "nenhuma materia encontrada para sua turma": "No subjects found for your class",
      "erro ao carregar suas notas": "Error loading your grades",
      "falha ao buscar turmas": "Failed to fetch classes",
      "falha ao buscar alunos": "Failed to fetch students",
      "nenhum aluno encontrado para essa turma": "No students found for this class",
      "selecione a materia e a turma": "Select the subject and class",
      "as notas foram salvas apenas neste navegador": "Grades were saved only in this browser. Use 'Publish grades' to record in the system.",
      "erro ao publicar notas": "Error publishing grades",
      "selecione a materia e a turma.": "Select the subject and class.",
      "erro ao carregar materias.": "Error loading subjects.",
      "falha ao buscar turmas.": "Failed to fetch classes.",
      "falha ao buscar alunos.": "Failed to fetch students.",
      "erro ao carregar alunos.": "Error loading students.",
      "nenhum aluno encontrado para essa turma.": "No students found for this class.",
      "erro ao publicar notas.": "Error publishing grades.",
      "selecione um curso uma materia e uma turma para carregar os alunos.": "Select a course, subject, and class to load students.",
      "selecione a data da aula": "Select the class date",
      "selecione a data da aula.": "Select the class date.",
      "nenhum aluno carregado para salvar": "No students loaded to save",
      "nenhum aluno carregado para salvar.": "No students loaded to save.",
      "erro ao salvar presenca": "Error saving attendance",
      "chamada salva com sucesso": "Roll call saved successfully",
      "chamada salva com sucesso.": "Roll call saved successfully.",
      "selecione a data": "Select the date",
      "evento adicionado": "Event added",
      "evento adicionado com sucesso": "Event added successfully",
      "evento atualizado": "Event updated",
      "evento atualizado com sucesso": "Event updated successfully",
      "erro ao adicionar evento": "Error adding event",
      "excluir evento": "Delete event",
      "excluir evento?": "Delete event?",
      "feriado": "Holiday",
      "reuniao": "Meeting",
      "outro": "Other",
      "o nome deve ter no minimo 3 caracteres": "The name must have at least 3 characters",
      "informe um cpf valido": "Enter a valid CPF",
      "informe um e-mail valido": "Enter a valid e-mail",
      "informe um telefone valido com ddd": "Enter a valid phone number with area code",
      "informe a data de nascimento": "Enter the date of birth",
      "informe um salario valido no formato 0,00": "Enter a valid salary in format 0.00",
      "nenhuma informacao foi alterada": "No information was changed",
      "usuario cadastrado": "User registered",
      "usuario atualizado": "User updated",
      "falha ao carregar dados do usuario": "Failed to load user data",
      "deseja excluir o usuario": "Delete this user?",
      "usuario excluido": "User deleted",
      "todos os alunos": "All students",
      "todos os professores": "All teachers",
      "acesse com suas credenciais institucionais": "Sign in with your institutional credentials",
      "sistema academico": "Academic System",
      "gerencie com": "Manage with",
      "acessar sistema →": "Access system →",
      "acessar o sistema →": "Access the system →",
      "visao geral": "Overview",
      "da instituicao": "of the institution",
      "media abaixo de 5,0": "Average below 5.0",
      "selecione curso materia turma e aluno para visualizar a frequencia": "Select course, subject, class, and student to view attendance",
      "selecione a materia turma e aluno para visualizar a frequencia": "Select subject, class, and student to view attendance"
    },
    es: {
      "acessar com suas credenciais institucionais": "Accede con tus credenciales institucionales",
      "acessar o sistema": "Acceder al sistema",
      "acessar o sistema ->": "Acceder al sistema ->",
      "acessar sistema ->": "Acceder al sistema ->",
      "acompanhe seu": "Acompaña tu",
      "academico": "académico",
      "academica": "académica",
      "acesso por perfil": "Acceso por perfil",
      "acesso seguro": "Acceso seguro",
      "acoes": "Acciones",
      "a acao nao pode ser desfeita": "Esta acción no se puede deshacer",
      "a especialidade deve ter no minimo 3 caracteres.": "La especialidad debe tener al menos 3 caracteres.",
      "a idade minima permitida e de 12 anos.": "La edad mínima permitida es de 12 años.",
      "a nova senha deve ter pelo menos 6 caracteres.": "La nueva contraseña debe tener al menos 6 caracteres.",
      "0,00": "0,00",
      "a senha inicial usa a data de nascimento no formato ddmmaa.": "La contraseña inicial usa la fecha de nacimiento en formato DDMMAA.",
      "a senha inicial usa a data de nascimento no formato DDMMAA.": "La contraseña inicial usa la fecha de nacimiento en formato DDMMAA.",
      "a data e hora de fim deve ter pelo menos 1 hora de diferenca do inicio.": "La fecha y hora de fin deben estar al menos 1 hora después del inicio.",
      "a data e hora de fim nao podem estar no passado.": "La fecha y hora de fin no pueden estar en el pasado.",
      "a data e hora de inicio nao podem estar no passado.": "La fecha y hora de inicio no pueden estar en el pasado.",
      "abrir detalhes": "Abrir detalles",
      "abril": "Abril",
      "agosto": "Agosto",
      "altere pelo menos um campo antes de salvar.": "Cambia al menos un campo antes de guardar.",
      "aluno": "Estudiante",
      "aluno(a)": "Estudiante",
      "alunos": "Estudiantes",
      "alunos devem ter mais de 12 anos.": "Los estudiantes deben tener más de 12 años.",
      "alunos matriculados": "Estudiantes matriculados",
      "apenas alunos": "Solo estudiantes",
      "apenas professores": "Solo profesores",
      "aprovados": "Aprobados",
      "ativas": "activas",
      "ativar modo escuro": "Activar modo oscuro",
      "atencao": "Atención",
      "atribuir professor": "Asignar profesor",
      "aulas": "Clases",
      "buscar": "Buscar",
      "bem-vindo,": "Bienvenido,",
      "bem-vindo(a) de volta": "Bienvenido(a) de nuevo",
      "calendario": "Calendario",
      "cancelar": "Cancelar",
      "capacidade": "Capacidad",
      "carregando...": "Cargando...",
      "carregando notas...": "Cargando notas...",
      "codigo": "Código",
      "codigo:": "Código:",
      "com precisao": "con precisión",
      "confirmar": "Confirmar",
      "coordenacao": "Coordinación",
      "cor": "Color",
      "corrija as notas abaixo antes de continuar:": "Corrige las notas siguientes antes de continuar:",
      "cpf": "CPF",
      "curso": "Curso",
      "cursos": "Cursos",
      "cadastrados": "registrados",
      "cadastre e gerencie alunos, professores e coordenadores com controle de acesso por papel.": "Registra y gestiona estudiantes, profesores y coordinadores con control de acceso por rol.",
      "cada usuario ve apenas o que e relevante para seu papel - coordenador, professor ou aluno.": "Cada usuario ve solo lo relevante para su rol: coordinador, profesor o estudiante.",
      "cada usuario ve apenas o que e relevante para seu papel — coordenador, professor ou aluno.": "Cada usuario ve solo lo relevante para su rol: coordinador, profesor o estudiante.",
      "comunicados": "Comunicados",
      "data": "Fecha",
      "data / hora inicio *": "Fecha / hora inicio *",
      "data de nascimento": "Fecha de nacimiento",
      "dados pessoais": "Datos personales",
      "de presenca nas aulas": "de asistencia en clases",
      "desenvolvedora": "Desarrolladora",
      "desenvolvedor": "Desarrollador",
      "dezembro": "Diciembre",
      "desempenho": "Rendimiento",
      "desempenho e": "rendimiento y",
      "desativar modo escuro": "Desactivar modo oscuro",
      "descrição": "Descripción",
      "detalhes opcionais...": "Detalles opcionales...",
      "digite sua senha atual": "Escribe tu contraseña actual",
      "digite sua senha atual para continuar.": "Escribe tu contraseña actual para continuar.",
      "disciplinas": "asignaturas",
      "e-mail": "Correo",
      "editar": "Editar",
      "editar curso": "Editar curso",
      "editar dados da turma": "Editar datos del grupo",
      "editar perfil": "Editar perfil",
      "em alerta": "en alerta",
      "em atencao": "En atención",
      "entrar na plataforma": "Entrar a la plataforma",
      "entrega": "Entrega",
      "equipe": "Equipo",
      "erro": "Error",
      "erro ao buscar cursos.": "Error al buscar cursos.",
      "erro ao carregar dados do usuario.": "Error al cargar datos del usuario.",
      "erro ao carregar eventos.": "Error al cargar eventos.",
      "erro ao carregar notas.": "Error al cargar notas.",
      "erro ao carregar professores.": "Error al cargar profesores.",
      "erro ao carregar suas notas.": "Error al cargar tus notas.",
      "evolua": "evoluciona",
      "escolha": "Elige",
      "escolher mes/ano": "elegir mes/año",
      "esqueceu a sua senha?": "¿Olvidaste tu contraseña?",
      "especialidade": "Especialidad",
      "evento pessoal (visivel so para mim)": "Evento personal (visible solo para mí)",
      "ex.: analise e desenvolvimento de sistemas": "Ej.: Análisis y Desarrollo de Sistemas",
      "ex.: matematica": "Ej.: Matemáticas",
      "ex.: prova de poo": "Ej.: Examen de POO",
      "ex.: joao da silva": "Ej.: Juan Pérez",
      "excluir": "Eliminar",
      "excluir curso": "Eliminar curso",
      "exporte relatorios de frequencia individuais por aluno, materia e periodo com um clique.": "Exporta informes individuales de asistencia por estudiante, asignatura y periodo con un clic.",
      "falha ao buscar cursos.": "Fallo al buscar cursos.",
      "falha ao buscar materias.": "Fallo al buscar asignaturas.",
      "falha ao buscar notas.": "Fallo al buscar notas.",
      "falha ao buscar professores.": "Fallo al buscar profesores.",
      "falha ao conectar com o servidor.": "Fallo al conectar con el servidor.",
      "falha ao salvar": "Fallo al guardar",
      "falha na conexao": "Fallo de conexión",
      "falha na conexao.": "Fallo de conexión.",
      "fazer login": "Iniciar sesión",
      "fechar": "Cerrar",
      "fevereiro": "Febrero",
      "filtre suas materias e acompanhe da menor para a maior frequencia": "Filtra tus asignaturas y acompaña de menor a mayor asistencia",
      "filtrar matriculados...": "Filtrar matriculados...",
      "faltam": "Faltan",
      "faltas": "Faltas",
      "frequencia": "Asistencia",
      "frequencia geral dentro do esperado.": "Asistencia general dentro de lo esperado.",
      "frequencia geral institucional.": "Asistencia media institucional.",
      "frequencia maior para menor": "Asistencia de mayor a menor",
      "frequencia menor para maior": "Asistencia de menor a mayor",
      "frequencia regular": "Asistencia regular",
      "frequencias e notas sempre atualizadas": "Asistencias y notas siempre actualizadas",
      "frequencias, notas e comunicados reunidos em uma plataforma moderna para alunos, professores e coordenadores.": "Asistencias, notas y comunicados reunidos en una plataforma moderna para estudiantes, profesores y coordinadores.",
      "ferramentas projetadas para simplificar a gestao academica do inicio ao fim.": "Herramientas diseñadas para simplificar la gestión académica de principio a fin.",
      "funcionalidades": "Funcionalidades",
      "gerencie alunos, professores e coordenadores": "Gestiona estudiantes, profesores y coordinadores",
      "gerencie turmas": "Gestiona grupos",
      "gestao completa de turmas, professores, alunos e desempenho academico": "Gestión completa de grupos, profesores, estudiantes y rendimiento académico",
      "gestao de usuarios": "Gestión de usuarios",
      "hoje": "Hoy",
      "idioma": "Idioma",
      "idade invalida": "Edad inválida",
      "inicio": "Inicio",
      "informe a data de nascimento.": "Informa la fecha de nacimiento.",
      "informe um cpf valido.": "Informa un CPF válido.",
      "informe um e-mail valido.": "Informa un correo válido.",
      "informe um salario valido no formato 0,00.": "Informa un salario válido en formato 0,00.",
      "informe um telefone valido com ddd.": "Informa un teléfono válido con código de área.",
      "inteligencia": "inteligencia",
      "janeiro": "Enero",
      "julho": "Julio",
      "junho": "Junio",
      "leciona": "enseña",
      "limpar": "Limpiar",
      "login": "Inicio de sesión",
      "marco": "Marzo",
      "materia": "Asignatura",
      "materia em ordem alfabetica": "Asignatura en orden alfabético",
      "materias": "Asignaturas",
      "matriculados": "matriculados",
      "maio": "Mayo",
      "media": "Promedio",
      "media da turma": "Promedio del grupo",
      "media geral da turma": "Promedio general del grupo",
      "media geral das disciplinas": "Promedio general de las asignaturas",
      "media geral instituicao": "Promedio general de la institución",
      "monitore o": "Monitorea el",
      "mensagens": "Mensajes",
      "mensagens e comunicados": "Mensajes y comunicados",
      "mensagens recentes": "Mensajes recientes",
      "minha frequencia": "Mi asistencia",
      "minha turma": "Mi grupo",
      "minimizar menu": "Minimizar menú",
      "monitore o desempenho academico com precisao": "Monitorea el rendimiento académico con precisión",
      "nascimento": "Nacimiento",
      "nenhum aluno encontrado para essa selecao.": "No se encontró ningún estudiante para esta selección.",
      "nenhum aluno matriculado.": "Ningún estudiante matriculado.",
      "nenhuma informacao foi alterada.": "Ninguna información fue modificada.",
      "nenhuma materia encontrada": "Ninguna asignatura encontrada",
      "nenhuma materia vinculada.": "Ninguna asignatura vinculada.",
      "nenhuma mensagem.": "Ningún mensaje.",
      "nenhum resultado encontrado": "Ningún resultado encontrado",
      "nome": "Nombre",
      "nome completo": "Nombre completo",
      "notas": "Notas",
      "nova senha": "Nueva contraseña",
      "o ano e sempre o corrente e nao pode ser alterado": "El año siempre es el actual y no se puede modificar",
      "o monitora+ centraliza frequencias, notas e mensagens em uma plataforma intuitiva para professores, coordenadores e alunos.": "Monitora+ centraliza asistencias, notas y mensajes en una plataforma intuitiva para profesores, coordinadores y estudiantes.",
      "o nome deve ter no minimo 3 caracteres.": "El nombre debe tener al menos 3 caracteres.",
      "outubro": "Octubre",
      "pagina inicial": "Inicio",
      "painel de gestao": "Panel de gestión",
      "periodo": "Periodo",
      "perfil": "Perfil",
      "perfis de acesso - aluno, professor e coordenacao": "Perfiles de acceso: estudiante, profesor y coordinación",
      "perfis de acesso — aluno, professor e coordenacao": "Perfiles de acceso: estudiante, profesor y coordinación",
      "pesquisar": "Buscar",
      "pesquisar materia": "Buscar asignatura",
      "pesquise o aluno": "Busca el estudiante",
      "pesquise o curso": "Busca el curso",
      "pesquise o professor": "Busca el profesor",
      "pesquise a materia": "Busca la asignatura",
      "pesquise a turma": "Busca el grupo",
      "plataforma academica": "Plataforma académica",
      "preencha apenas se quiser alterar a senha": "Completa solo si quieres cambiar la contraseña",
      "preencha e-mail, senha atual e nova senha.": "Completa correo, contraseña actual y nueva contraseña.",
      "presenca": "Asistencia",
      "pronto para comecar?": "¿Listo para comenzar?",
      "projeto desenvolvido por estudantes comprometidos com a inovacao na educacao.": "Proyecto desarrollado por estudiantes comprometidos con la innovación en la educación.",
      "professor": "Profesor",
      "professor nao informado": "Profesor no informado",
      "professores": "Profesores",
      "professores e coordenadores devem ter mais de 18 anos.": "Profesores y coordinadores deben tener más de 18 años.",
      "prova": "Examen",
      "publique mensagens vinculadas as materias para que alunos sejam notificados diretamente em suas turmas.": "Publica mensajes vinculados a las asignaturas para que los estudiantes sean notificados directamente en sus grupos.",
      "qua": "MIÉ",
      "rascunho salvo": "Borrador guardado",
      "real-time": "Tiempo real",
      "registre presencas e faltas por materia e turma, com visualizacao grafica do percentual de frequencia.": "Registra presencias y faltas por asignatura y grupo, con visualización gráfica del porcentaje de asistencia.",
      "relatorios para download": "Informes para descargar",
      "remover": "Eliminar",
      "remover professor": "Eliminar profesor",
      "sair": "Salir",
      "salario": "Salario",
      "salario (r$)": "Salario (R$)",
      "salvar": "Guardar",
      "salvar alteracoes": "Guardar cambios",
      "seguranca": "Seguridad",
      "selecione": "Selecciona",
      "selecione a materia": "Selecciona la asignatura",
      "selecione a turma": "Selecciona el grupo",
      "selecione professor, turma e materia para visualizar as notas.": "Selecciona profesor, grupo y asignatura para ver las notas.",
      "selecione um curso": "Selecciona un curso",
      "selecione o aluno": "Selecciona el estudiante",
      "selecione o curso": "Selecciona el curso",
      "selecione o professor": "Selecciona el profesor",
      "selecione uma turma": "Selecciona un grupo",
      "sem alertas disponiveis.": "Sin alertas disponibles.",
      "sem dados": "Sin datos",
      "sem notas": "Sin notas",
      "senha": "Contraseña",
      "sessao protegida": "Sesión protegida",
      "sua senha": "Tu contraseña",
      "suas notas, frequencia e agenda reunidos num so painel": "Tus notas, asistencia y agenda reunidos en un solo panel",
      "sistema de monitoramento academico": "Sistema de monitoreo académico",
      "sucesso": "Éxito",
      "telefone": "Teléfono",
      "titulo *": "Título *",
      "todos": "Todos",
      "todos (alunos e professores)": "Todos (estudiantes y profesores)",
      "todos os direitos reservados": "Todos los derechos reservados",
      "tudo que voce precisa em um so lugar": "Todo lo que necesitas en un solo lugar",
      "todas as materias": "Todas las asignaturas",
      "total": "total",
      "total de aulas": "Total de clases",
      "turma": "Grupo",
      "turmas ativas": "Grupos activos",
      "turmas em que voce leciona": "Grupos en los que enseñas",
      "turmas": "Grupos",
      "use:": "Usa:",
      "usuario": "Usuario",
      "usuarios": "Usuarios",
      "ver funcionalidades": "Ver funcionalidades",
      "ver todas": "Ver todas",
      "ver turmas": "Ver grupos",
      "visao geral da instituicao": "Vista general de la institución",
      "visao geral de todas as turmas ativas": "Vista general de todos los grupos activos",
      "visualizar": "Visualizar",
      "visivel para": "Visible para",
      "carregando sua frequencia...": "Cargando tu asistencia...",
      "digite a nova senha": "Escribe la nueva contraseña",
      "frequencia do aluno": "Asistencia del Estudiante",
      "frequencia insuficiente - abaixo do minimo exigido (75%)": "Asistencia insuficiente - por debajo del mínimo requerido (75%)",
      "frequencia regular - acima do minimo exigido (75%)": "Asistencia regular - por encima del mínimo requerido (75%)",
      "nao foi possivel carregar sua frequencia. tente novamente.": "No fue posible cargar tu asistencia. Inténtalo de nuevo.",
      "selecione a materia, turma e aluno para visualizar a frequencia": "Selecciona asignatura, grupo y estudiante para ver la asistencia",
      "selecione curso, materia, turma e aluno para visualizar a frequencia": "Selecciona curso, asignatura, grupo y estudiante para ver la asistencia",
      "1o semestre": "1.er semestre",
      "2o semestre": "2.º semestre",
      "a 100": "a 100",
      "abaixo do minimo exigido de 75%": "Por debajo del mínimo requerido del 75%",
      "acesso negado": "Acceso denegado",
      "agenda da semana": "Agenda Semanal",
      "alertas": "Alertas",
      "alertas de frequencia": "Alertas de asistencia",
      "alternar tema": "Alternar tema",
      "aluno:": "Estudiante:",
      "alunos abaixo de 75%": "Estudiantes por debajo del 75%",
      "alunos sob responsabilidade": "Estudiantes a tu cargo",
      "ano": "Año",
      "aprovado em": "Aprobado en",
      "as notas serao registradas e ficarao visiveis para os alunos.": "Las notas serán registradas y quedarán visibles para los estudiantes.",
      "atencao a frequencia": "Advertencia de asistencia",
      "ativa": "Activa",
      "ativo": "Activo",
      "aula": "Clase",
      "ausente": "Ausente",
      "aviso": "Aviso",
      "ainda nao ha medias calculadas.": "Aún no hay promedios calculados.",
      "buscar por nome ou codigo...": "Buscar por nombre o código...",
      "cadastre, edite e gerencie as disciplinas da instituicao": "Registra, edita y gestiona las asignaturas de la institución",
      "cadastre, edite e gerencie os cursos disponiveis na instituicao": "Registra, edita y gestiona los cursos disponibles",
      "carga horaria": "Carga horaria",
      "carga horaria (h)": "Carga horaria (h)",
      "carregando alunos...": "Cargando estudiantes...",
      "carregando cursos...": "Cargando cursos...",
      "carregando materias...": "Cargando asignaturas...",
      "carregando mensagens...": "Cargando mensajes...",
      "carregando suas turmas...": "Cargando tus grupos...",
      "chamada incompleta": "Asistencia incompleta",
      "colegas de turma": "Compañeros de grupo",
      "coordenador": "Coordinador",
      "criar turma": "Crear grupo",
      "curso atualizado!": "¡Curso actualizado!",
      "curso cadastrado!": "¡Curso registrado!",
      "curso removido.": "Curso eliminado.",
      "data / hora": "Fecha / hora",
      "data / hora fim": "Fecha / hora de fin",
      "data / hora inicio": "Fecha / hora de inicio",
      "data da aula": "Fecha de clase",
      "descricao": "Descripción",
      "descricao (opcional)": "Descripción (opcional)",
      "desempenho medio por turma": "Rendimiento medio por grupo",
      "desempenho por turma": "Rendimiento por grupo",
      "detalhe do evento": "Detalles del evento",
      "disciplinas cursando": "Asignaturas en curso",
      "distribuicao de usuarios": "Distribución de usuarios",
      "dom": "Dom",
      "editar turma": "Editar grupo",
      "enviado!": "¡Enviado!",
      "enviados": "Enviados",
      "enviar mensagem": "Enviar mensaje",
      "erro ao carregar cursos.": "Error al cargar cursos.",
      "erro ao salvar presenca.": "Error al guardar la asistencia.",
      "esta area e exclusiva para coordenadores.": "Esta área es exclusiva para coordinadores.",
      "evento": "Evento",
      "evento criado!": "¡Evento creado!",
      "excluida!": "¡Eliminada!",
      "excluido!": "¡Eliminado!",
      "excluir curso?": "¿Eliminar curso?",
      "excluir materia?": "¿Eliminar asignatura?",
      "expandir menu": "Expandir menú",
      "falha de conexao. tente novamente.": "Fallo de conexión. Inténtalo de nuevo.",
      "falha de conexao ao carregar cursos.": "Fallo de conexión al cargar cursos.",
      "falha de conexao ao carregar materias.": "Fallo de conexión al cargar asignaturas.",
      "faltando:": "Faltando:",
      "formato invalido": "Formato inválido",
      "frequencia critica": "Asistencia crítica",
      "frequencia geral": "Asistencia general",
      "frequencia media institucional.": "Asistencia media institucional.",
      "frequencia:": "Asistencia:",
      "gerencie alunos, materias e professores": "Gestiona estudiantes, asignaturas y profesores",
      "gerencie turmas e acompanhe o progresso": "Gestiona grupos y sigue el progreso",
      "gerir": "Gestionar",
      "gerir turma": "Gestionar grupo",
      "gestao de cursos": "Gestión de cursos",
      "gestao de materias": "Gestión de asignaturas",
      "inativa": "Inactiva",
      "inativo": "Inactivo",
      "informe a carga horaria.": "Ingresa la carga horaria.",
      "informe o codigo.": "Ingresa el código.",
      "informe o nome da materia.": "Ingresa el nombre de la asignatura.",
      "informe o nome do curso.": "Ingresa el nombre del curso.",
      "informe o prefixo.": "Ingresa el prefijo.",
      "informe uma carga horaria valida (min. 1h).": "Ingresa una carga horaria válida (mín. 1h).",
      "lancamento de notas": "Registro de notas",
      "leram": "leyeron",
      "mais": "más",
      "manha": "Mañana",
      "marque presenca ou ausencia para todos os alunos antes de salvar.": "Marca presente o ausente para todos los estudiantes antes de guardar.",
      "materia atualizada!": "¡Asignatura actualizada!",
      "materia cadastrada!": "¡Asignatura registrada!",
      "materia removida.": "Asignatura eliminada.",
      "materia:": "Asignatura:",
      "media geral": "Promedio general",
      "mensagem": "Mensaje",
      "mes anterior": "Mes anterior",
      "minhas materias": "Mis asignaturas",
      "minhas notas": "Mis notas",
      "nenhum alerta no momento.": "Ninguna alerta por el momento.",
      "nenhum aluno em alerta.": "Ningún estudiante en alerta.",
      "nenhum dado foi alterado.": "Ningún dato fue modificado.",
      "nenhuma alteracao": "Sin cambios",
      "nenhuma materia atribuida.": "Ninguna asignatura asignada.",
      "nenhuma materia encontrada para sua turma.": "Ninguna asignatura encontrada para tu grupo.",
      "nenhuma mensagem recente.": "Ningún mensaje reciente.",
      "nenhuma opcao disponivel": "Ninguna opción disponible",
      "nenhuma turma.": "Ningún grupo.",
      "nenhuma turma encontrada com esses filtros.": "Ningún grupo encontrado con estos filtros.",
      "nenhum curso cadastrado ainda.": "Ningún curso registrado aún.",
      "nenhum curso encontrado para a busca.": "Ningún curso encontrado.",
      "nenhuma materia cadastrada ainda.": "Ninguna asignatura registrada aún.",
      "nenhuma materia encontrada para a busca.": "Ninguna asignatura encontrada.",
      "noite": "Noche",
      "nome da materia": "Nombre de asignatura",
      "nome do curso": "Nombre del curso",
      "nota 1": "Nota 1",
      "nota 2": "Nota 2",
      "notas, frequencias e alertas das suas turmas em tempo real": "Notas, asistencia y alertas de tus grupos en tiempo real",
      "notas ainda nao lancadas pelo professor.": "Notas aún no registradas por el profesor.",
      "notas incompletas": "Notas incompletas",
      "notas por materia": "Notas por asignatura",
      "notas por turma": "Notas por grupo",
      "notas publicadas!": "¡Notas publicadas!",
      "nova materia": "Nueva asignatura",
      "nova mensagem": "Nuevo mensaje",
      "nova turma": "Nuevo grupo",
      "novo curso": "Nuevo curso",
      "o codigo deve ter pelo menos 2 caracteres.": "El código debe tener al menos 2 caracteres.",
      "o nome deve ter pelo menos 3 caracteres.": "El nombre debe tener al menos 3 caracteres.",
      "o prefixo deve ter pelo menos 2 caracteres.": "El prefijo debe tener al menos 2 caracteres.",
      "para quem": "Para quién",
      "periodo:": "Periodo:",
      "prefixo / codigo": "Prefijo / Código",
      "prefixo / sigla": "Prefijo / Sigla",
      "presente": "Presente",
      "previa gerada automaticamente": "Vista previa generada automáticamente",
      "proximo mes": "Mes siguiente",
      "publicar notas": "Publicar notas",
      "publicar notas?": "¿Publicar notas?",
      "quem desenvolveu o monitora+": "Quién desarrolló Monitora+",
      "qui": "Jue",
      "recebidos": "Recibidos",
      "relatorio de frequencia": "Informe de Asistencia",
      "responsavel": "Responsable",
      "sab": "Sáb",
      "salvar chamada": "Guardar asistencia",
      "salvar rascunho": "Guardar borrador",
      "salvando...": "Guardando...",
      "seg": "Lun",
      "selecione a turma primeiro": "Selecciona primero el grupo",
      "selecione apenas dias uteis (segunda a sexta).": "Selecciona solo días hábiles (lunes a viernes).",
      "selecione curso, materia e turma para registrar as notas": "Selecciona curso, asignatura y grupo para registrar notas",
      "selecione curso, materia, turma e data para carregar os alunos.": "Selecciona curso, asignatura, grupo y fecha para cargar estudiantes.",
      "selecione curso, materia, turma e data para registrar a chamada": "Selecciona curso, asignatura, grupo y fecha para registrar asistencia",
      "selecione curso, professor, turma e materia para visualizar as notas": "Selecciona curso, profesor, grupo y asignatura para ver notas",
      "selecione o professor primeiro": "Selecciona primero el profesor",
      "selecione os dados - nome e codigo serao gerados automaticamente": "Selecciona los datos — el nombre y código se generarán automáticamente",
      "selecione os dados — nome e codigo serao gerados automaticamente": "Selecciona los datos — el nombre y código se generarán automáticamente",
      "selecione um curso, uma materia e uma turma para carregar os alunos.": "Selecciona un curso, asignatura y grupo para cargar estudiantes.",
      "sem dados.": "Sin datos.",
      "sem descricao": "Sin descripción",
      "sera removida permanentemente.": "será eliminada permanentemente.",
      "sera removido permanentemente.": "será eliminado permanentemente.",
      "sex": "Vie",
      "sim, publicar": "Sí, publicar",
      "situacoes que precisam de atencao": "Situaciones que requieren atención",
      "sua turma e colegas matriculados": "Tu grupo y compañeros matriculados",
      "suas notas e medias por materia": "Tus notas y promedios por asignatura",
      "tarde": "Tarde",
      "ter": "Mar",
      "tipo": "Tipo",
      "titulo": "Título",
      "todos os cursos": "Todos los cursos",
      "todos os periodos": "Todos los periodos",
      "todos os turnos": "Todos los turnos",
      "total de aulas:": "Total de clases:",
      "turma / periodo": "Grupo / Periodo",
      "turno": "Turno",
      "ver detalhes": "Ver detalles",
      "© 2026 · todos os direitos reservados": "© 2026 · Todos los derechos reservados",
      "voltar ao inicio": "Volver al inicio",
      "adicionar evento": "Agregar evento",
      "adicionar usuario": "Agregar usuario",
      "aprovado": "Aprobado",
      "a mensagem deve ter mais de 3 caracteres": "El mensaje debe tener más de 3 caracteres",
      "carregando cursos": "Cargando cursos...",
      "carregando materias": "Cargando materias...",
      "chamada": "Lista",
      "codigo do curso": "Código del curso",
      "confira os dados antes de confirmar o envio": "Confirme los datos antes de enviar",
      "data de fim": "Fecha de fin",
      "data de inicio": "Fecha de inicio",
      "descricao do curso": "Descripción del curso",
      "deseja enviar a mensagem": "¿Enviar mensaje?",
      "erro ao carregar mensagens": "Error al cargar mensajes",
      "escreva a mensagem": "Escriba el mensaje",
      "falha na conexao com o servidor": "Fallo de conexión con el servidor",
      "gerar relatorio": "Generar informe",
      "historico de frequencia": "Historial de asistencia",
      "nenhuma mensagem enviada": "No hay mensajes enviados",
      "nenhuma mensagem recebida": "No hay mensajes recibidos",
      "o titulo deve ter mais de 3 caracteres": "El título debe tener más de 3 caracteres",
      "papel": "Rol",
      "preencha o titulo": "Complete el título",
      "registro de presenca": "Registro de asistencia",
      "reprovado": "Reprobado",
      "reprovados": "Reprobados",
      "selecione o coordenador": "Seleccione el coordinador",
      "selecione para quem enviar": "Seleccione a quién enviar",
      "sem cursos cadastrados": "Sin cursos registrados",
      "situacao": "Situación",
      "titulo do evento": "Título del evento",
      "tipo de evento": "Tipo de evento",
      "voce": "tú",
      "carregando": "Cargando...",
      "carregando dados": "Cargando datos...",
      "erro ao carregar cursos": "Error al cargar cursos",
      "erro ao carregar materias": "Error al cargar materias",
      "excluido": "¡Eliminado!",
      "falha de conexao": "Fallo de conexión",
      "falha de conexao tente novamente": "Fallo de conexión. Inténtalo de nuevo.",
      "nenhum curso cadastrado ainda": "Aún no hay cursos registrados",
      "nenhum curso encontrado para a busca": "No se encontraron cursos para la búsqueda",
      "nenhum dado foi alterado": "No se cambió ningún dato",
      "nenhum resultado": "Sin resultados",
      "nota lancada com sucesso": "Calificación registrada exitosamente",
      "nota atualizada com sucesso": "Calificación actualizada exitosamente",
      "nota atualizada": "Calificación actualizada",
      "nenhuma alteracao detectada": "No se detectaron cambios",
      "salvando": "Guardando...",
      "salvo": "Guardado",
      "curso removido": "Curso eliminado",
      "esta area e exclusiva para coordenadores": "Esta área es exclusiva para coordinadores",
      "sim excluir": "Sí, eliminar",
      "sim salvar": "Sí, guardar",
      "sim enviar": "Sí, enviar",
      "nenhum aluno matriculado": "No hay alumnos matriculados",
      "erro ao carregar dados": "Error al cargar datos",
      "sem professor": "Sin profesor",
      "professor(es)": "Profesor(es)",
      "carregando alunos": "Cargando alumnos...",
      "nenhum aluno encontrado": "No se encontraron alumnos",
      "tipo aula": "Tipo de clase",
      "marcar todos presentes": "Marcar todos presentes",
      "marcar todos ausentes": "Marcar todos ausentes",
      "buscar usuario": "Buscar usuario",
      "filtrar por papel": "Filtrar por rol",
      "nenhum usuario encontrado": "No se encontraron usuarios",
      "todos os papeis": "Todos los roles",
      "excluir turma?": "¿Eliminar clase?",
      "pesquise e selecione um aluno da lista.": "Busque y seleccione un alumno de la lista.",
      "pesquise e selecione uma materia da lista.": "Busque y seleccione una materia de la lista.",
      "pesquise e selecione um professor da lista.": "Busque y seleccione un profesor de la lista.",
      "sera desvinculado dessa turma.": "será desvinculado de esta clase.",
      "deseja desmatricular": "¿Dar de baja al alumno?",
      "desvincular": "Desvincular",
      "professor removido": "Profesor eliminado",
      "prefixo invalido.": "Prefijo no válido.",
      "nome do curso invalido.": "Nombre del curso no válido.",
      "carregando notas": "Cargando calificaciones...",
      "erro ao carregar notas": "Error al cargar calificaciones",
      "nenhuma materia encontrada para sua turma": "No se encontraron materias para tu clase",
      "erro ao carregar suas notas": "Error al cargar tus calificaciones",
      "falha ao buscar turmas": "Error al buscar clases",
      "falha ao buscar alunos": "Error al buscar alumnos",
      "nenhum aluno encontrado para essa turma": "No se encontraron alumnos para esta clase",
      "selecione a materia e a turma": "Seleccione la materia y la clase",
      "as notas foram salvas apenas neste navegador": "Las calificaciones se guardaron solo en este navegador. Use 'Publicar notas' para registrar en el sistema.",
      "selecione a materia e a turma.": "Seleccione la materia y la clase.",
      "erro ao carregar materias.": "Error al cargar materias.",
      "falha ao buscar turmas.": "Error al buscar clases.",
      "falha ao buscar alunos.": "Error al buscar alumnos.",
      "erro ao carregar alunos.": "Error al cargar alumnos.",
      "nenhum aluno encontrado para essa turma.": "No se encontraron alumnos para esta clase.",
      "erro ao publicar notas.": "Error al publicar calificaciones.",
      "selecione um curso uma materia e uma turma para carregar os alunos.": "Seleccione un curso, materia y clase para cargar alumnos.",
      "selecione a data da aula": "Seleccione la fecha de la clase",
      "selecione a data da aula.": "Seleccione la fecha de la clase.",
      "nenhum aluno carregado para salvar": "No hay alumnos cargados para guardar",
      "nenhum aluno carregado para salvar.": "No hay alumnos cargados para guardar.",
      "erro ao salvar presenca": "Error al guardar asistencia",
      "chamada salva com sucesso": "Lista guardada exitosamente",
      "chamada salva com sucesso.": "Lista guardada exitosamente.",
      "selecione a data": "Seleccione la fecha",
      "evento adicionado": "Evento agregado",
      "evento adicionado com sucesso": "Evento agregado exitosamente",
      "evento atualizado": "Evento actualizado",
      "evento atualizado com sucesso": "Evento actualizado exitosamente",
      "erro ao adicionar evento": "Error al agregar evento",
      "excluir evento": "Eliminar evento",
      "excluir evento?": "¿Eliminar evento?",
      "feriado": "Festivo",
      "reuniao": "Reunión",
      "outro": "Otro",
      "o nome deve ter no minimo 3 caracteres": "El nombre debe tener al menos 3 caracteres",
      "informe um cpf valido": "Ingresa un CPF válido",
      "informe um e-mail valido": "Ingresa un correo válido",
      "informe um telefone valido com ddd": "Ingresa un teléfono válido con código de área",
      "informe a data de nascimento": "Ingresa la fecha de nacimiento",
      "nenhuma informacao foi alterada": "Ninguna información fue modificada",
      "usuario cadastrado": "Usuario registrado",
      "usuario atualizado": "Usuario actualizado",
      "falha ao carregar dados do usuario": "Error al cargar datos del usuario",
      "deseja excluir o usuario": "¿Eliminar este usuario?",
      "usuario excluido": "Usuario eliminado",
      "todos os alunos": "Todos los alumnos",
      "todos os professores": "Todos los profesores",
      "acesse com suas credenciais institucionais": "Accede con tus credenciales institucionales",
      "sistema academico": "Sistema Académico",
      "gerencie com": "Gestiona con",
      "acessar sistema →": "Acceder al sistema →",
      "acessar o sistema →": "Acceder al sistema →",
      "visao geral": "Resumen",
      "da instituicao": "de la institución",
      "media abaixo de 5,0": "Promedio por debajo de 5,0",
      "selecione a materia turma e aluno para visualizar a frequencia": "Seleccione materia, clase y alumno para ver asistencia"
    }
  };

  Object.assign(TEXT.en, {
    "a materia sera removida desta turma.": "The subject will be removed from this class.",
    "acesse o sistema com suas credenciais institucionais.": "Access the system with your institutional credentials.",
    "altere os dados da turma": "Change class data",
    "aluno removido!": "Student removed!",
    "as notas foram salvas apenas neste navegador. use 'publicar notas' para registrar no sistema.": "Grades were saved only in this browser. Use 'Publish grades' to record them in the system.",
    "assunto da mensagem": "Message subject",
    "breve descricao da disciplina...": "Brief subject description...",
    "carregando sua turma": "Loading your class...",
    "carregando sua turma...": "Loading your class...",
    "clique para escolher mes/ano": "Click to choose month/year",
    "controle de frequencia": "Attendance control",
    "da": "of the",
    "desvincular materia": "Unlink subject",
    "desvincular materia?": "Unlink subject?",
    "digite o conteudo da mensagem...": "Type the message content...",
    "erro ao atribuir.": "Error assigning.",
    "erro ao criar turma.": "Error creating class.",
    "erro ao enviar.": "Error sending.",
    "erro ao salvar.": "Error saving.",
    "escreva a mensagem.": "Write the message.",
    "falha de conexao.": "Connection failure.",
    "faltas:": "Absences:",
    "formato invalido. use: 7 ou 7,5 ou 7,50 (max 2 casas decimais, entre 0 e 10)": "Invalid format. Use: 7, 7.5, or 7.50 (up to 2 decimal places, from 0 to 10)",
    "(max 2 casas decimais, de 0 a 10).": "(up to 2 decimal places, from 0 to 10).",
    "freq.": "Att.",
    "instituicao": "institution",
    "materia removida!": "Subject removed!",
    "monitora+ | calendario": "Monitora+ | Calendar",
    "monitora+ | cursos": "Monitora+ | Courses",
    "monitora+ | frequencia": "Monitora+ | Attendance",
    "monitora+ | gestao de usuarios": "Monitora+ | User Management",
    "monitora+ | inicio": "Monitora+ | Home",
    "monitora+ | login": "Monitora+ | Login",
    "monitora+ | materias": "Monitora+ | Subjects",
    "monitora+ | mensagens": "Monitora+ | Messages",
    "monitora+ | notas": "Monitora+ | Grades",
    "monitora+ | perfil": "Monitora+ | Profile",
    "monitora+ | presenca": "Monitora+ | Attendance",
    "monitora+ | sistema de monitoramento academico": "Monitora+ | Academic Monitoring System",
    "monitora+ | turmas": "Monitora+ | Classes",
    "nao foi possivel excluir.": "Could not delete.",
    "nenhum dado encontrado.": "No data found.",
    "nenhuma informacao foi modificada.": "No information was changed.",
    "o aluno sera desmatriculado desta turma.": "The student will be removed from this class.",
    "o progresso": "progress",
    "observacoes: professor, utilize este campo para justificar uma falta especifica": "Notes: teacher, use this field to justify a specific absence",
    "operacao realizada com sucesso.": "Operation completed successfully.",
    "ou": "or",
    "para publicar, todos os alunos precisam ter as duas notas preenchidas.": "To publish, every student must have both grades filled in.",
    "alunos sem nota:": "Students without grades:",
    "preencha o titulo.": "Fill in the title.",
    "presencas": "Presences",
    "presencas:": "Presences:",
    "professores lancam e publicam notas por avaliacao. medias calculadas automaticamente com indicacao de aprovacao.": "Teachers enter and publish grades by assessment. Averages are calculated automatically with approval status.",
    "receba e envie comunicados para sua turma": "Receive and send announcements for your class",
    "remover aluno?": "Remove student?",
    "selecione o coordenador.": "Select the coordinator.",
    "selecione o professor.": "Select the teacher.",
    "selecione para quem enviar.": "Select who should receive it.",
    "semestre": "semester",
    "turma criada!": "Class created!",
    "visualize e registre aulas, provas e eventos": "View and register classes, exams, and events",
    "web — acesso de qualquer lugar": "Web - access from anywhere",
    "web - acesso de qualquer lugar": "Web - access from anywhere",
    // Turmas
    "turma excluida!": "Class deleted!",
    "erro ao excluir turma.": "Error deleting class.",
    "matriculado!": "Enrolled!",
    "erro ao matricular.": "Error enrolling.",
    "materia vinculada!": "Subject linked!",
    "atribua um professor abaixo se necessario.": "Assign a teacher below if needed.",
    "erro ao vincular.": "Error linking.",
    "professor atribuido!": "Teacher assigned!",
    "professor removido!": "Teacher removed!",
    "sem alteracoes": "No changes",
    "turma atualizada!": "Class updated!",
    "erro ao editar turma.": "Error editing class.",
    "selecione um curso.": "Select a course.",
    "selecione o periodo.": "Select the period.",
    "informe a capacidade.": "Enter the capacity.",
    "capacidade deve ser entre 1 e 100.": "Capacity must be between 1 and 100.",
    "falha na conexao com o servidor.": "Connection to server failed.",
    "erro ao carregar turmas.": "Error loading classes.",
    "erro ao carregar sua turma.": "Error loading your class.",
    // Mensagens
    "erro ao carregar mensagens.": "Error loading messages.",
    "nenhuma mensagem recebida.": "No messages received.",
    "nenhuma mensagem enviada.": "No messages sent.",
    "nenhum coordenador encontrado": "No coordinator found",
    "selecione a turma.": "Select the class.",
    "selecione a materia.": "Select the subject.",
    "o titulo deve ter mais de 3 caracteres.": "The title must have more than 3 characters.",
    "a mensagem deve ter mais de 3 caracteres.": "The message must have more than 3 characters.",
    "deseja enviar a mensagem?": "Do you want to send the message?",
    "confira os dados antes de confirmar o envio.": "Check the data before confirming the send.",
    "sim, enviar": "Yes, send",
    "enviando...": "Sending...",
    // Calendario
    "novo evento": "New event",
    "editar evento": "Edit event",
    "global (todas as turmas)": "Global (all classes)",
    "selecione a turma...": "Select the class...",
    "selecione primeiro a turma": "Select the class first",
    "selecione a materia...": "Select the subject...",
    "evento pessoal": "Personal event",
    "geral": "General",
    "falha ao carregar eventos.": "Failed to load events.",
    "preencha titulo e data de inicio.": "Fill in the title and start date.",
    "o titulo deve ter no minimo 3 caracteres.": "The title must have at least 3 characters.",
    "informe uma data e hora de inicio valida.": "Enter a valid start date and time.",
    "informe uma data e hora de fim valida.": "Enter a valid end date and time.",
    "selecione uma turma para o evento.": "Select a class for the event.",
    "selecione uma materia para o evento.": "Select a subject for the event.",
    "nenhum dado foi atualizado.": "No data was updated.",
    "salvar alteracoes?": "Save changes?",
    "deseja realmente editar este evento?": "Do you really want to edit this event?",
    "sim, editar": "Yes, edit",
    "erro ao salvar evento.": "Error saving event.",
    "evento atualizado!": "Event updated!",
    "esta acao nao pode ser desfeita.": "This action cannot be undone.",
    "evento removido!": "Event removed!",
    "erro ao excluir.": "Error deleting.",
    "visivel so para mim": "Visible only to me",
    "criado por mim": "Created by me",
    // Gestao usuarios
    "nenhum registro encontrado.": "No records found.",
    "erro ao carregar dados.": "Error loading data.",
    "nenhum resultado para a busca.": "No results for the search.",
    "erro ao buscar dados.": "Error searching data.",
    "novo aluno": "New student",
    "novo professor": "New teacher",
    "novo coordenador": "New coordinator",
    "novo usuario": "New user",
    "editar usuario": "Edit user",
    "excluir usuario?": "Delete user?",
    "essa acao nao podera ser desfeita.": "This action cannot be undone.",
    "sim, excluir": "Yes, delete",
    "nova senha:": "New password:",
    "senha inicial:": "Initial password:",
    "falha ao carregar dados do usuario.": "Failed to load user data.",
    // Perfil
    "nome invalido": "Invalid name",
    "o nome deve ter pelo menos 3 letras.": "The name must have at least 3 letters.",
    "e-mail invalido": "Invalid e-mail",
    "digite um e-mail valido, contendo @ e dominio.": "Enter a valid email with @ and domain.",
    "telefone invalido": "Invalid phone number",
    "digite um telefone com ddd, no formato (xx)xxxxx-xxxx.": "Enter a phone number with area code, format (xx)xxxxx-xxxx.",
    "data obrigatoria": "Required date",
    "nao foi possivel carregar os dados do perfil.": "Could not load profile data.",
    "nenhum dado foi atualizado": "No data was updated",
    "confirme sua senha atual": "Confirm your current password",
    "para alterar a senha, digite sua senha atual.": "To change the password, enter your current password.",
    "senha atual": "Current password",
    "deseja realmente alterar os dados do perfil?": "Do you really want to change your profile data?",
    "sim, salvar": "Yes, save",
    "nao foi possivel atualizar o perfil.": "Could not update the profile.",
    "perfil atualizado!": "Profile updated!",
    "erro inesperado": "Unexpected error",
    "nao foi possivel conectar ao servidor.": "Could not connect to the server.",
    // Autenticacao
    "campos obrigatorios": "Required fields",
    "informe seu e-mail e sua senha.": "Enter your email and password.",
    "erro no login": "Login error",
    "e-mail ou senha invalidos.": "Invalid email or password.",
    "login realizado!": "Login successful!",
    "bem-vindo(a),": "Welcome,",
    "alterar senha": "Change password",
    "nao foi possivel alterar": "Could not change",
    "verifique os dados informados.": "Check the information entered.",
    "senha alterada": "Password changed",
    "sua senha foi atualizada com sucesso.": "Your password was updated successfully.",
    "ocultar senha": "Hide password",
    "mostrar senha": "Show password",
    // Comum
    "deseja sair?": "Do you want to sign out?",
    "sua sessao sera encerrada.": "Your session will be terminated.",
    "sim, sair": "Yes, sign out",
    "bem-vindo(a) de volta": "Welcome back"
  });

  Object.assign(TEXT.es, {
    "a materia sera removida desta turma.": "La asignatura será eliminada de este grupo.",
    "a turma sera desativada esta acao nao pode ser desfeita.": "El grupo será desactivado. Esta acción no se puede deshacer.",
    "acesse o sistema com suas credenciais institucionais.": "Accede al sistema con tus credenciales institucionales.",
    "altere os dados da turma": "Modifica los datos del grupo",
    "aluno removido!": "¡Estudiante eliminado!",
    "alunos matriculados · materias e professores": "Estudiantes matriculados · Asignaturas y profesores",
    "as notas foram salvas apenas neste navegador. use 'publicar notas' para registrar no sistema.": "Las notas se guardaron solo en este navegador. Usa 'Publicar notas' para registrarlas en el sistema.",
    "assunto da mensagem": "Asunto del mensaje",
    "breve descricao da disciplina...": "Breve descripción de la asignatura...",
    "carregando sua turma": "Cargando tu grupo...",
    "carregando sua turma...": "Cargando tu grupo...",
    "carregando turmas": "Cargando grupos...",
    "carregando turmas...": "Cargando grupos...",
    "clique para escolher mes/ano": "Haz clic para elegir mes/año",
    "controle de frequencia": "Control de asistencia",
    "da": "de la",
    "desvincular materia": "Desvincular asignatura",
    "desvincular materia?": "¿Desvincular asignatura?",
    "digite o conteudo da mensagem...": "Escribe el contenido del mensaje...",
    "editar materia": "Editar asignatura",
    "erro ao atribuir.": "Error al asignar.",
    "erro ao carregar turmas": "Error al cargar grupos",
    "erro ao criar turma.": "Error al crear el grupo.",
    "erro ao enviar.": "Error al enviar.",
    "erro ao publicar notas": "Error al publicar notas",
    "erro ao salvar.": "Error al guardar.",
    "escreva a mensagem.": "Escribe el mensaje.",
    "excluir materia": "Eliminar asignatura",
    "falha de conexao.": "Fallo de conexión.",
    "faltas:": "Faltas:",
    "formato invalido. use: 7 ou 7,5 ou 7,50 (max 2 casas decimais, entre 0 e 10)": "Formato inválido. Usa: 7, 7,5 o 7,50 (máximo 2 decimales, entre 0 y 10)",
    "(max 2 casas decimais, de 0 a 10).": "(máximo 2 decimales, de 0 a 10).",
    "freq.": "Asist.",
    "gerencie alunos materias e professores": "Gestiona estudiantes, asignaturas y profesores",
    "informe um salario valido no formato 0,00": "Informa un salario válido en formato 0,00",
    "instituicao": "institución",
    "materia removida": "Asignatura eliminada",
    "materia removida!": "¡Asignatura eliminada!",
    "monitora+ | calendario": "Monitora+ | Calendario",
    "monitora+ | cursos": "Monitora+ | Cursos",
    "monitora+ | frequencia": "Monitora+ | Asistencia",
    "monitora+ | gestao de usuarios": "Monitora+ | Gestión de Usuarios",
    "monitora+ | inicio": "Monitora+ | Inicio",
    "monitora+ | login": "Monitora+ | Inicio de sesión",
    "monitora+ | materias": "Monitora+ | Asignaturas",
    "monitora+ | mensagens": "Monitora+ | Mensajes",
    "monitora+ | notas": "Monitora+ | Notas",
    "monitora+ | perfil": "Monitora+ | Perfil",
    "monitora+ | presenca": "Monitora+ | Asistencia",
    "monitora+ | sistema de monitoramento academico": "Monitora+ | Sistema de Monitoreo Académico",
    "monitora+ | turmas": "Monitora+ | Grupos",
    "nao foi possivel excluir.": "No fue posible eliminar.",
    "nenhum dado encontrado.": "No se encontraron datos.",
    "nenhuma informacao foi modificada.": "Ninguna información fue modificada.",
    "nenhuma materia cadastrada ainda": "Aún no hay asignaturas registradas",
    "nenhuma materia vinculada": "No hay asignaturas vinculadas",
    "nenhuma turma encontrada com esses filtros": "No se encontraron grupos con esos filtros",
    "notas publicadas": "Notas publicadas",
    "o aluno sera desmatriculado desta turma.": "El estudiante será retirado de este grupo.",
    "o progresso": "el progreso",
    "observacoes: professor, utilize este campo para justificar uma falta especifica": "Observaciones: profesor, utiliza este campo para justificar una falta específica",
    "operacao realizada com sucesso.": "Operación realizada con éxito.",
    "ou": "o",
    "para publicar, todos os alunos precisam ter as duas notas preenchidas.": "Para publicar, todos los estudiantes deben tener las dos notas completas.",
    "alunos sem nota:": "Estudiantes sin nota:",
    "preencha o titulo.": "Completa el título.",
    "presencas": "Asistencias",
    "presencas:": "Asistencias:",
    "professores lancam e publicam notas por avaliacao. medias calculadas automaticamente com indicacao de aprovacao.": "Los profesores registran y publican notas por evaluación. Los promedios se calculan automáticamente con indicación de aprobación.",
    "receba e envie comunicados para sua turma": "Recibe y envía comunicados para tu grupo",
    "remover aluno?": "¿Remover estudiante?",
    "selecione curso materia e turma para registrar as notas": "Selecciona curso, asignatura y grupo para registrar las notas",
    "selecione curso materia turma e aluno para visualizar a frequencia": "Selecciona curso, asignatura, grupo y estudiante para ver la asistencia",
    "selecione curso professor turma e materia para visualizar as notas": "Selecciona curso, profesor, grupo y asignatura para ver las notas",
    "selecione o coordenador.": "Selecciona el coordinador.",
    "selecione o professor.": "Selecciona el profesor.",
    "selecione para quem enviar.": "Selecciona a quién enviar.",
    "selecionar materia": "Seleccionar asignatura",
    "selecionar turma": "Seleccionar grupo",
    "sem materias cadastradas": "Sin asignaturas registradas",
    "semestre": "semestre",
    "turma atualizada": "Grupo actualizado",
    "turma atualizada com sucesso!": "¡Grupo actualizado con éxito!",
    "turma criada": "Grupo creado",
    "turma criada!": "¡Grupo creado!",
    "turma criada com sucesso!": "¡Grupo creado con éxito!",
    "turma editada com sucesso!": "¡Grupo actualizado con éxito!",
    "visualize e registre aulas, provas e eventos": "Visualiza y registra clases, pruebas y eventos",
    "web — acesso de qualquer lugar": "Web - acceso desde cualquier lugar",
    "web - acesso de qualquer lugar": "Web - acceso desde cualquier lugar",
    // Turmas
    "turma excluida!": "¡Grupo eliminado!",
    "erro ao excluir turma.": "Error al eliminar el grupo.",
    "matriculado!": "¡Matriculado!",
    "erro ao matricular.": "Error al matricular.",
    "materia vinculada!": "¡Asignatura vinculada!",
    "atribua um professor abaixo se necessario.": "Asigna un profesor abajo si es necesario.",
    "erro ao vincular.": "Error al vincular.",
    "professor atribuido!": "¡Profesor asignado!",
    "professor removido!": "¡Profesor eliminado!",
    "sem alteracoes": "Sin cambios",
    "turma atualizada!": "¡Grupo actualizado!",
    "erro ao editar turma.": "Error al editar el grupo.",
    "selecione um curso.": "Selecciona un curso.",
    "selecione o periodo.": "Selecciona el período.",
    "informe a capacidade.": "Informa la capacidad.",
    "capacidade deve ser entre 1 e 100.": "La capacidad debe estar entre 1 y 100.",
    "falha na conexao com o servidor.": "Fallo de conexión con el servidor.",
    "erro ao carregar turmas.": "Error al cargar grupos.",
    "erro ao carregar sua turma.": "Error al cargar tu grupo.",
    // Mensagens
    "erro ao carregar mensagens.": "Error al cargar mensajes.",
    "nenhuma mensagem recebida.": "No hay mensajes recibidos.",
    "nenhuma mensagem enviada.": "No hay mensajes enviados.",
    "nenhum coordenador encontrado": "No se encontró coordinador",
    "selecione a turma.": "Selecciona el grupo.",
    "selecione a materia.": "Selecciona la asignatura.",
    "o titulo deve ter mais de 3 caracteres.": "El título debe tener más de 3 caracteres.",
    "a mensagem deve ter mais de 3 caracteres.": "El mensaje debe tener más de 3 caracteres.",
    "deseja enviar a mensagem?": "¿Deseas enviar el mensaje?",
    "confira os dados antes de confirmar o envio.": "Verifica los datos antes de confirmar el envío.",
    "sim, enviar": "Sí, enviar",
    "enviando...": "Enviando...",
    // Calendario
    "novo evento": "Nuevo evento",
    "editar evento": "Editar evento",
    "global (todas as turmas)": "Global (todos los grupos)",
    "selecione a turma...": "Selecciona el grupo...",
    "selecione primeiro a turma": "Selecciona primero el grupo",
    "selecione a materia...": "Selecciona la asignatura...",
    "evento pessoal": "Evento personal",
    "geral": "General",
    "falha ao carregar eventos.": "Error al cargar eventos.",
    "preencha titulo e data de inicio.": "Completa el título y la fecha de inicio.",
    "o titulo deve ter no minimo 3 caracteres.": "El título debe tener al menos 3 caracteres.",
    "informe uma data e hora de inicio valida.": "Indica una fecha y hora de inicio válida.",
    "informe uma data e hora de fim valida.": "Indica una fecha y hora de fin válida.",
    "selecione uma turma para o evento.": "Selecciona un grupo para el evento.",
    "selecione uma materia para o evento.": "Selecciona una asignatura para el evento.",
    "nenhum dado foi atualizado.": "No se actualizó ningún dato.",
    "salvar alteracoes?": "¿Guardar cambios?",
    "deseja realmente editar este evento?": "¿Realmente deseas editar este evento?",
    "sim, editar": "Sí, editar",
    "erro ao salvar evento.": "Error al guardar el evento.",
    "evento atualizado!": "¡Evento actualizado!",
    "esta acao nao pode ser desfeita.": "Esta acción no se puede deshacer.",
    "evento removido!": "¡Evento eliminado!",
    "erro ao excluir.": "Error al eliminar.",
    "visivel so para mim": "Visible solo para mí",
    "criado por mim": "Creado por mí",
    // Gestao usuarios
    "nenhum registro encontrado.": "No se encontraron registros.",
    "erro ao carregar dados.": "Error al cargar datos.",
    "nenhum resultado para a busca.": "No hay resultados para la búsqueda.",
    "erro ao buscar dados.": "Error al buscar datos.",
    "novo aluno": "Nuevo estudiante",
    "novo professor": "Nuevo profesor",
    "novo coordenador": "Nuevo coordinador",
    "novo usuario": "Nuevo usuario",
    "editar usuario": "Editar usuario",
    "excluir usuario?": "¿Eliminar usuario?",
    "essa acao nao podera ser desfeita.": "Esta acción no podrá deshacerse.",
    "sim, excluir": "Sí, eliminar",
    "nova senha:": "Nueva contraseña:",
    "senha inicial:": "Contraseña inicial:",
    "falha ao carregar dados do usuario.": "Error al cargar datos del usuario.",
    // Perfil
    "nome invalido": "Nombre inválido",
    "o nome deve ter pelo menos 3 letras.": "El nombre debe tener al menos 3 letras.",
    "e-mail invalido": "Correo inválido",
    "digite um e-mail valido, contendo @ e dominio.": "Ingresa un correo válido con @ y dominio.",
    "telefone invalido": "Teléfono inválido",
    "digite um telefone com ddd, no formato (xx)xxxxx-xxxx.": "Ingresa un teléfono con código de área, formato (xx)xxxxx-xxxx.",
    "data obrigatoria": "Fecha obligatoria",
    "nao foi possivel carregar os dados do perfil.": "No se pudieron cargar los datos del perfil.",
    "nenhum dado foi atualizado": "Ningún dato fue actualizado",
    "confirme sua senha atual": "Confirma tu contraseña actual",
    "para alterar a senha, digite sua senha atual.": "Para cambiar la contraseña, ingresa tu contraseña actual.",
    "senha atual": "Contraseña actual",
    "deseja realmente alterar os dados do perfil?": "¿Realmente deseas cambiar los datos del perfil?",
    "sim, salvar": "Sí, guardar",
    "nao foi possivel atualizar o perfil.": "No se pudo actualizar el perfil.",
    "perfil atualizado!": "¡Perfil actualizado!",
    "erro inesperado": "Error inesperado",
    "nao foi possivel conectar ao servidor.": "No fue posible conectar con el servidor.",
    // Autenticacao
    "campos obrigatorios": "Campos obligatorios",
    "informe seu e-mail e sua senha.": "Ingresa tu correo y contraseña.",
    "erro no login": "Error de inicio de sesión",
    "e-mail ou senha invalidos.": "Correo o contraseña inválidos.",
    "login realizado!": "¡Inicio de sesión exitoso!",
    "bem-vindo(a),": "¡Bienvenido/a,",
    "alterar senha": "Cambiar contraseña",
    "nao foi possivel alterar": "No fue posible cambiar",
    "verifique os dados informados.": "Verifica los datos ingresados.",
    "senha alterada": "Contraseña cambiada",
    "sua senha foi atualizada com sucesso.": "Tu contraseña fue actualizada con éxito.",
    "ocultar senha": "Ocultar contraseña",
    "mostrar senha": "Mostrar contraseña",
    // Comum
    "deseja sair?": "¿Deseas salir?",
    "sua sessao sera encerrada.": "Tu sesión será cerrada.",
    "sim, sair": "Sí, salir"
  });

  const INLINE_RULES = {
    en: [
      [/\bMédia\b/g, "Average"],
      [/\bmédia\b/g, "average"],
      [/\bNota\b/g, "Grade"],
      [/\bnota\b/g, "grade"],
      [/\bNotas\b/g, "Grades"],
      [/\bnotas\b/g, "grades"],
      [/\bAluno\(s\)\b/g, "Student(s)"],
      [/\baluno\(s\)\b/g, "student(s)"],
      [/\bAluno\b/g, "Student"],
      [/\baluno\b/g, "student"],
      [/\bAlunos\b/g, "Students"],
      [/\balunos\b/g, "students"],
      [/\bProfessor\b/g, "Teacher"],
      [/\bprofessor\b/g, "teacher"],
      [/\bMatéria\b/g, "Subject"],
      [/\bmatéria\b/g, "subject"],
      [/\bMateria\b/g, "Subject"],
      [/\bmateria\b/g, "subject"],
      [/\bTurma\b/g, "Class"],
      [/\bturma\b/g, "class"],
      [/\bPeríodo\b/g, "Period"],
      [/\bPeriodo\b/g, "Period"],
      [/\bperíodo\b/g, "period"],
      [/\bperiodo\b/g, "period"],
      [/\bCódigo\b/g, "Code"],
      [/\bCodigo\b/g, "Code"],
      [/\bcurso\b/g, "course"],
      [/\bcursos\b/g, "courses"],
      [/\bpresença\b/g, "attendance"],
      [/\bPresença\b/g, "Attendance"],
      [/\bFrequência\b/g, "Attendance"],
      [/\bfrequência\b/g, "attendance"],
      [/\bfrequencia\b/g, "attendance"],
      [/\bPresencas\b/g, "Presences"],
      [/\bPresenças\b/g, "Presences"],
      [/\bFaltas\b/g, "Absences"],
      [/\bsemestre\b/g, "semester"],
      [/\btotal\b/g, "total"],
      [/\bBoa\b/g, "Good"],
      [/\bAtenção\b/g, "Attention"],
      [/\bAtencao\b/g, "Attention"],
      [/\bCrítica\b/g, "Critical"],
      [/\bCritica\b/g, "Critical"],
      [/Bem-vindo\(a\)/g, "Welcome"],
      [/\bBom dia\b/g, "Good morning"],
      [/\bBoa tarde\b/g, "Good afternoon"],
      [/\bBoa noite\b/g, "Good evening"],
      [/\bManhã\b/g, "Morning"],
      [/\bmanhã\b/g, "morning"],
      [/\bManha\b/g, "Morning"],
      [/\bmanha\b/g, "morning"],
      [/\bNoite\b/g, "Evening"],
      [/\bnoite\b/g, "evening"],
      [/\bTarde\b/g, "Afternoon"],
      [/\btarde\b/g, "afternoon"],
      [/\bAno\b/g, "Year"],
      [/\bano\b/g, "year"],
      [/\bAnos\b/g, "Years"],
      [/\banos\b/g, "years"],
      [/\bTurno\b/g, "Shift"],
      [/\bturno\b/g, "shift"],
      [/\bEditar\b/g, "Edit"],
      [/\beditar\b/g, "edit"],
      [/\bGerir\b/g, "Manage"],
      [/\bgerir\b/g, "manage"],
      [/\bAviso\b/g, "Notice"],
      [/\baviso\b/g, "notice"],
      [/\bPresente\b/g, "Present"],
      [/\bpresente\b/g, "present"],
      [/\bAusente\b/g, "Absent"],
      [/\bausente\b/g, "absent"],
      [/\bCoordenador\b/g, "Coordinator"],
      [/\bcoordenador\b/g, "coordinator"],
      [/\bEnviados\b/g, "Sent"],
      [/\bRecebidos\b/g, "Received"],
      [/\bAulas\b/g, "Classes"],
      [/\baulas\b/g, "classes"]
    ],
    es: [
      [/\bMédia\b/g, "Promedio"],
      [/\bmédia\b/g, "promedio"],
      [/\bNota\b/g, "Nota"],
      [/\bnota\b/g, "nota"],
      [/\bNotas\b/g, "Notas"],
      [/\bnotas\b/g, "notas"],
      [/\bAluno\(s\)\b/g, "Estudiante(s)"],
      [/\baluno\(s\)\b/g, "estudiante(s)"],
      [/\bAluno\b/g, "Estudiante"],
      [/\baluno\b/g, "estudiante"],
      [/\bAlunos\b/g, "Estudiantes"],
      [/\balunos\b/g, "estudiantes"],
      [/\bProfessor\b/g, "Profesor"],
      [/\bprofessor\b/g, "profesor"],
      [/\bMatéria\b/g, "Asignatura"],
      [/\bmatéria\b/g, "asignatura"],
      [/\bMateria\b/g, "Asignatura"],
      [/\bmateria\b/g, "asignatura"],
      [/\bTurma\b/g, "Grupo"],
      [/\bturma\b/g, "grupo"],
      [/\bPeríodo\b/g, "Periodo"],
      [/\bPeriodo\b/g, "Periodo"],
      [/\bperíodo\b/g, "periodo"],
      [/\bperiodo\b/g, "periodo"],
      [/\bCódigo\b/g, "Código"],
      [/\bCodigo\b/g, "Código"],
      [/\bcurso\b/g, "curso"],
      [/\bcursos\b/g, "cursos"],
      [/\bpresença\b/g, "asistencia"],
      [/\bPresença\b/g, "Asistencia"],
      [/\bFrequência\b/g, "Asistencia"],
      [/\bfrequência\b/g, "asistencia"],
      [/\bfrequencia\b/g, "asistencia"],
      [/\bPresencas\b/g, "Asistencias"],
      [/\bPresenças\b/g, "Asistencias"],
      [/\bFaltas\b/g, "Faltas"],
      [/\bsemestre\b/g, "semestre"],
      [/\bBoa\b/g, "Buena"],
      [/\bAtenção\b/g, "Atención"],
      [/\bAtencao\b/g, "Atención"],
      [/\bCrítica\b/g, "Crítica"],
      [/\bCritica\b/g, "Crítica"],
      [/Bem-vindo\(a\)/g, "Bienvenido(a)"],
      [/\bBom dia\b/g, "Buenos días"],
      [/\bBoa tarde\b/g, "Buenas tardes"],
      [/\bBoa noite\b/g, "Buenas noches"],
      [/\bManhã\b/g, "Mañana"],
      [/\bmanhã\b/g, "mañana"],
      [/\bManha\b/g, "Mañana"],
      [/\bmanha\b/g, "mañana"],
      [/\bNoite\b/g, "Noche"],
      [/\bnoite\b/g, "noche"],
      [/\bTarde\b/g, "Tarde"],
      [/\btarde\b/g, "tarde"],
      [/\bAno\b/g, "Año"],
      [/\bano\b/g, "año"],
      [/\bAnos\b/g, "Años"],
      [/\banos\b/g, "años"],
      [/\bTurno\b/g, "Turno"],
      [/\bturno\b/g, "turno"],
      [/\bEditar\b/g, "Editar"],
      [/\beditar\b/g, "editar"],
      [/\bGerir\b/g, "Gestionar"],
      [/\bgerir\b/g, "gestionar"],
      [/\bAviso\b/g, "Aviso"],
      [/\baviso\b/g, "aviso"],
      [/\bPresente\b/g, "Presente"],
      [/\bpresente\b/g, "presente"],
      [/\bAusente\b/g, "Ausente"],
      [/\bausente\b/g, "ausente"],
      [/\bCoordenador\b/g, "Coordinador"],
      [/\bcoordenador\b/g, "coordinador"],
      [/\bEnviados\b/g, "Enviados"],
      [/\bRecebidos\b/g, "Recibidos"],
      [/\bAulas\b/g, "Clases"],
      [/\baulas\b/g, "clases"]
    ]
  };

  function normalizeKey(value) {
    return String(value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/\s+/g, " ")
      .trim()
      .toLowerCase();
  }

  function readLanguage() {
    const stored = [STORAGE_KEY, ...LEGACY_KEYS]
      .map((key) => {
        try { return window.localStorage.getItem(key); } catch (_) { return null; }
      })
      .find(Boolean);
    return normalizeLanguage(stored || DEFAULT_LANGUAGE);
  }

  function normalizeLanguage(value) {
    const raw = String(value || "").trim().toLowerCase();
    if (raw.startsWith("en")) return "en";
    if (raw.startsWith("es")) return "es";
    return "pt";
  }

  function getLanguage() {
    return currentLanguage;
  }

  function getLocale() {
    return SUPPORTED_LANGUAGES[currentLanguage]?.locale || SUPPORTED_LANGUAGES.pt.locale;
  }

  function saveLanguage(language) {
    currentLanguage = normalizeLanguage(language);
    try {
      window.localStorage.setItem(STORAGE_KEY, currentLanguage);
      window.localStorage.setItem("monitora.lang", currentLanguage);
    } catch (_) {}
  }

  function preserveWhitespace(source, translated) {
    const value = String(source);
    const start = value.match(/^\s*/)?.[0] || "";
    const end = value.match(/\s*$/)?.[0] || "";
    return `${start}${translated}${end}`;
  }

  function exactTranslation(value, language = currentLanguage) {
    if (language === "pt") return value;
    const raw = String(value || "");
    const trimmed = raw.trim();
    if (!trimmed) return value;

    const dictionary = TEXT[language] || {};
    const key = normalizeKey(trimmed);
    const translated = dictionary[key] || dictionary[key.replace(/[.!?,;:]+$/, "")];
    if (translated) return preserveWhitespace(raw, translated);

    if (trimmed.includes("|")) {
      const parts = trimmed.split("|").map((part) => part.trim());
      const nextParts = parts.map((part) => dictionary[normalizeKey(part)] || part);
      const joined = nextParts.join(" | ");
      if (joined !== trimmed) return preserveWhitespace(raw, joined);
    }

    return value;
  }

  function translateInline(value, language = currentLanguage) {
    const numeric = translateNumericText(value, language);
    if (numeric !== value) return numeric;

    const exact = exactTranslation(value, language);
    if (exact !== value || language === "pt") return exact;

    let translated = String(value || "");
    const rules = INLINE_RULES[language] || [];
    for (const [pattern, replacement] of rules) {
      translated = translated.replace(pattern, replacement);
    }
    return translated;
  }

  function translateNumericText(value, language = currentLanguage) {
    const raw = String(value || "");
    const trimmed = raw.trim();
    if (!trimmed) return value;

    const money = trimmed.match(/^R\$\s*(-?\d+(?:[.,]\d{1,2})?)$/);
    if (money) {
      const decimals = (money[1].split(/[.,]/)[1] || "").length || 2;
      const number = parseNumber(money[1]);
      if (number !== null) {
        return preserveWhitespace(raw, `R$ ${formatNumber(number, {
          minimumFractionDigits: decimals,
          maximumFractionDigits: decimals,
          useGrouping: false
        })}`);
      }
    }

    const decimal = trimmed.match(/^-?\d+[.,]\d{1,2}$/);
    if (decimal) {
      const decimals = (trimmed.split(/[.,]/)[1] || "").length;
      const number = parseNumber(trimmed);
      if (number !== null) {
        return preserveWhitespace(raw, formatNumber(number, {
          minimumFractionDigits: decimals,
          maximumFractionDigits: decimals,
          useGrouping: false
        }));
      }
    }

    return value;
  }

  function translate(value, language = currentLanguage) {
    return translateInline(value, language);
  }

  function translateHtmlFragment(value, language = currentLanguage) {
    const raw = String(value || "");
    if (!raw.trim()) return value;
    if (!raw.includes("<") || !raw.includes(">")) return translate(raw, language);
    if (typeof document === "undefined") return translate(raw, language);

    const template = document.createElement("template");
    template.innerHTML = raw;

    const walker = document.createTreeWalker(template.content, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        return node.nodeValue && node.nodeValue.trim()
          ? NodeFilter.FILTER_ACCEPT
          : NodeFilter.FILTER_REJECT;
      }
    });

    let node = walker.nextNode();
    while (node) {
      node.nodeValue = translate(node.nodeValue, language);
      node = walker.nextNode();
    }

    return template.innerHTML;
  }

  function shouldSkipNode(node) {
    const element = node.nodeType === Node.ELEMENT_NODE ? node : node.parentElement;
    if (!element) return true;
    return Boolean(element.closest("script, style, template, svg, canvas, #avatarUsuario, #nomeUsuarioTopo, [data-i18n-ignore], [data-i18n-dynamic]"));
  }

  function translateTextNode(node) {
    if (!node || shouldSkipNode(node)) return;

    const current = node.nodeValue || "";
    if (!current.trim()) return;

    const last = textLastTranslated.get(node);
    if (!textOriginals.has(node) || (last !== undefined && current !== last)) {
      textOriginals.set(node, current);
    }

    const original = textOriginals.get(node) || current;
    const translated = translate(original);
    textLastTranslated.set(node, translated);

    if (current !== translated) {
      node.nodeValue = translated;
    }
  }

  function getAttrStore(store, element) {
    if (!store.has(element)) store.set(element, {});
    return store.get(element);
  }

  function translateAttribute(element, attrName) {
    if (!element.hasAttribute(attrName) || shouldSkipNode(element)) return;

    const current = element.getAttribute(attrName) || "";
    if (!current.trim()) return;

    const originals = getAttrStore(attrOriginals, element);
    const lastTranslated = getAttrStore(attrLastTranslated, element);

    if (!Object.prototype.hasOwnProperty.call(originals, attrName)
      || (lastTranslated[attrName] !== undefined && current !== lastTranslated[attrName])) {
      originals[attrName] = current;
    }

    const translated = translate(originals[attrName]);
    lastTranslated[attrName] = translated;
    if (current !== translated) element.setAttribute(attrName, translated);
  }

  function translateElementAttributes(root) {
    const attrs = ["placeholder", "title", "aria-label", "alt", "data-empty-text"];
    const elements = root.nodeType === Node.ELEMENT_NODE
      ? [root, ...root.querySelectorAll(attrs.map((attr) => `[${attr}]`).join(","))]
      : [];

    for (const element of elements) {
      for (const attr of attrs) translateAttribute(element, attr);
    }
  }

  function translateTree(root = document.body) {
    if (!root) return;
    translating = true;
    try {
      translateElementAttributes(root);

      const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
        acceptNode(node) {
          return shouldSkipNode(node) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT;
        }
      });

      let node = walker.nextNode();
      while (node) {
        translateTextNode(node);
        node = walker.nextNode();
      }

      translateDocumentTitle();
      ensureLanguageControl();
    } finally {
      translating = false;
    }
  }

  function translateDocumentTitle() {
    if (!document.title) return;
    const last = translateDocumentTitle.lastTranslated;
    if (!originalTitle || (last !== undefined && document.title !== last)) {
      originalTitle = document.title;
    }
    const translated = translate(originalTitle);
    translateDocumentTitle.lastTranslated = translated;
    if (document.title !== translated) document.title = translated;
  }

  function setDocumentLanguage() {
    const meta = SUPPORTED_LANGUAGES[currentLanguage] || SUPPORTED_LANGUAGES.pt;
    document.documentElement.lang = meta.htmlLang;
  }

  function installStyles() {
    if (document.getElementById("monitora-i18n-style")) return;
    const style = document.createElement("style");
    style.id = "monitora-i18n-style";
    style.textContent = `
      .i18n-language-select {
        height: 38px;
        min-width: 70px;
        border: 1.5px solid rgba(147, 215, 223, 0.45);
        border-radius: 999px;
        background: var(--white, #fff);
        color: var(--mid, #577284);
        font: 700 0.78rem 'Sora', sans-serif;
        padding: 0 12px;
        outline: none;
        cursor: pointer;
        box-shadow: 0 2px 12px rgba(76, 190, 190, 0.12);
      }
      .i18n-language-select:focus {
        border-color: var(--accent, #4caebe);
        box-shadow: 0 0 0 3px rgba(76, 190, 190, 0.12);
      }
      body.dark .i18n-language-select {
        background: #122436;
        color: #dff8fb;
        border-color: rgba(147, 215, 223, 0.24);
      }
      .nav-actions .i18n-language-select { flex-shrink: 0; }
      .inicio-header .i18n-language-select { margin-left: auto; }
      .inicio-header .i18n-language-select + .user-menu { margin-left: 8px; }
      @media (max-width: 680px) {
        .i18n-language-select { height: 34px; min-width: 64px; }
        .inicio-header .i18n-language-select { margin-left: 0; }
      }
      .swal2-popup .swal2-validation-message {
        background: rgba(229, 83, 83, 0.1) !important;
        color: #e06060 !important;
        border-top: 1px solid rgba(229, 83, 83, 0.2) !important;
        font-size: 0.85em !important;
        margin-top: 1em !important;
      }
      .swal2-popup .swal2-validation-message::before {
        background: #e06060 !important;
      }
      body.dark .swal2-popup .swal2-validation-message {
        background: rgba(229, 83, 83, 0.18) !important;
        color: #e87878 !important;
        border-top-color: rgba(229, 83, 83, 0.3) !important;
      }
      /* ── Flatpickr Monitora+ Theme ── */
      /* Calendar container */
      .flatpickr-calendar{
        background:#0f2030;border:1.5px solid rgba(76,190,190,.38);
        border-radius:18px;padding:0;width:312px;overflow:hidden;
        box-shadow:0 24px 64px rgba(0,0,0,.65),0 4px 20px rgba(76,190,190,.22);
        font-family:'DM Sans',sans-serif;
      }
      .flatpickr-calendar.open{z-index:99999;}
      .flatpickr-calendar::before,.flatpickr-calendar::after{display:none;}
      /* Header */
      .flatpickr-months{
        background:linear-gradient(135deg,#4caebe 0%,#237a8c 100%);
        border-radius:0;padding:2px 4px;
      }
      .flatpickr-months .flatpickr-month{color:#fff;fill:#fff;height:48px;line-height:48px;}
      .flatpickr-current-month{color:#fff;font-weight:700;font-size:.97rem;padding-top:13px;letter-spacing:.01em;}
      .flatpickr-current-month .flatpickr-monthDropdown-months{
        background:transparent;color:#fff;font-weight:700;border:none;
        padding:0 2px;font-size:.97rem;cursor:pointer;
      }
      .flatpickr-current-month .flatpickr-monthDropdown-months option{background:#0f2030;color:#9dcad8;}
      .flatpickr-current-month input.cur-year{color:#fff;font-weight:700;font-size:.97rem;}
      .flatpickr-months .flatpickr-prev-month,.flatpickr-months .flatpickr-next-month{padding:13px 14px;color:#fff;fill:#fff;}
      .flatpickr-months .flatpickr-prev-month svg,.flatpickr-months .flatpickr-next-month svg{fill:#fff;width:14px;height:14px;}
      .flatpickr-months .flatpickr-prev-month:hover,.flatpickr-months .flatpickr-next-month:hover{background:rgba(255,255,255,.2);border-radius:8px;}
      /* Weekday header row */
      .flatpickr-weekdays{background:rgba(76,190,190,.10);height:34px;align-items:center;border-bottom:1px solid rgba(76,190,190,.15);}
      .flatpickr-weekdaycontainer{width:100%;}
      span.flatpickr-weekday{color:#4caebe;font-weight:700;font-size:.68rem;letter-spacing:.06em;flex:1;text-align:center;}
      /* Days */
      .dayContainer{padding:6px 6px 8px;}
      .flatpickr-days{border:none;border-radius:0;}
      .flatpickr-day{
        color:#8dc8d8;border-radius:10px;height:38px;line-height:38px;
        max-width:38px;font-size:.88rem;font-weight:500;
        border:1.5px solid transparent;transition:all .15s ease;
      }
      .flatpickr-day:hover:not(.flatpickr-disabled):not(.selected){
        background:rgba(76,190,190,.18);border-color:rgba(76,190,190,.4);color:#fff;
      }
      .flatpickr-day.selected,.flatpickr-day.selected:hover{
        background:linear-gradient(135deg,#4caebe 0%,#237a8c 100%);
        border-color:transparent;color:#fff;font-weight:700;
        box-shadow:0 4px 14px rgba(76,190,190,.45);
      }
      .flatpickr-day.today{border-color:#4caebe!important;color:#4caebe;font-weight:700;}
      .flatpickr-day.today:not(.selected):hover{background:rgba(76,190,190,.2);color:#fff;}
      .flatpickr-day.prevMonthDay,.flatpickr-day.nextMonthDay{color:#2a4558;opacity:.8;}
      .flatpickr-day.flatpickr-disabled,.flatpickr-day.flatpickr-disabled:hover{color:#1c3446;opacity:.45;cursor:not-allowed;}
      /* Time picker */
      .flatpickr-time{
        height:50px;border-top:1px solid rgba(76,190,190,.15);
        background:rgba(76,190,190,.06);border-radius:0;
      }
      .flatpickr-time input{
        color:#8dc8d8;font-family:'DM Sans',sans-serif;font-weight:700;
        font-size:.98rem;background:transparent;border-radius:8px;
      }
      .flatpickr-time input:hover,.flatpickr-time input:focus{background:rgba(76,190,190,.12);}
      .flatpickr-time .flatpickr-time-separator{color:#4caebe;font-weight:700;}
      .flatpickr-time .numInputWrapper{height:100%;}
      .numInputWrapper:hover{background:rgba(76,190,190,.1);border-radius:8px;}
      .numInputWrapper span.arrowUp:after{border-bottom-color:#4caebe;}
      .numInputWrapper span.arrowDown:after{border-top-color:#4caebe;}
      /* Light mode overrides */
      body:not(.dark) .flatpickr-calendar{background:#f3fafc;border-color:rgba(76,190,190,.3);}
      body:not(.dark) .flatpickr-day{color:#1c4255;}
      body:not(.dark) .flatpickr-day:hover:not(.flatpickr-disabled):not(.selected){background:rgba(76,190,190,.14);color:#103040;}
      body:not(.dark) .flatpickr-day.prevMonthDay,body:not(.dark) .flatpickr-day.nextMonthDay{color:#92bece;opacity:.9;}
      body:not(.dark) .flatpickr-day.today{color:#1a7890;}
      body:not(.dark) .flatpickr-time{background:rgba(76,190,190,.08);}
      body:not(.dark) .flatpickr-time input{color:#1c4255;}
      body:not(.dark) .flatpickr-current-month .flatpickr-monthDropdown-months option{background:#f3fafc;color:#1c4255;}
      body:not(.dark) .flatpickr-day.flatpickr-disabled{color:#c0dce6;}
      /* Alt-input field */
      input.flatpickr-input.flatpickr-alt-input{cursor:pointer;}
    `;
    document.head.appendChild(style);
  }

  function createLanguageControl() {
    const select = document.createElement("select");
    select.className = "i18n-language-select";
    select.id = "monitoraLanguageSelect";
    select.setAttribute("aria-label", translate("Idioma"));
    select.title = translate("Idioma");
    select.dataset.i18nIgnore = "true";

    for (const [code, meta] of Object.entries(SUPPORTED_LANGUAGES)) {
      const option = document.createElement("option");
      option.value = code;
      option.textContent = meta.label;
      option.title = meta.name;
      select.appendChild(option);
    }

    select.value = currentLanguage;
    select.addEventListener("change", () => setLanguage(select.value));
    return select;
  }

  function ensureLanguageControl() {
    installStyles();
    const existing = document.getElementById("monitoraLanguageSelect");
    if (existing) {
      existing.value = currentLanguage;
      existing.setAttribute("aria-label", translate("Idioma"));
      existing.title = translate("Idioma");
      return;
    }

    const header = document.querySelector(".inicio-header");
    const navActions = document.querySelector(".nav-actions");
    const target = header || navActions;
    if (!target) return;

    const control = createLanguageControl();
    const themeButton = target.querySelector(".nav-theme-toggle");
    const userMenu = target.querySelector(".user-menu");

    if (header && userMenu) {
      header.insertBefore(control, userMenu);
    } else if (themeButton?.nextSibling) {
      target.insertBefore(control, themeButton.nextSibling);
    } else {
      target.appendChild(control);
    }
  }

  function installObserver() {
    if (observer || !window.MutationObserver || !document.body) return;
    observer = new MutationObserver((mutations) => {
      if (translating) return;
      let needsControl = false;

      for (const mutation of mutations) {
        if (mutation.type === "characterData") {
          translateTextNode(mutation.target);
        } else if (mutation.type === "attributes") {
          translateAttribute(mutation.target, mutation.attributeName);
        } else {
          for (const node of mutation.addedNodes) {
            if (node.nodeType === Node.ELEMENT_NODE) {
              translateTree(node);
              updateDateInputLang(node);
              needsControl = true;
            } else if (node.nodeType === Node.TEXT_NODE) {
              translateTextNode(node);
            }
          }
        }
      }

      if (needsControl) ensureLanguageControl();
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      characterData: true,
      attributes: true,
      attributeFilter: ["placeholder", "title", "aria-label", "alt", "data-empty-text"]
    });
  }

  function withObserverPaused(callback) {
    const activeObserver = observer;
    if (activeObserver) activeObserver.disconnect();
    try {
      return callback();
    } finally {
      observer = null;
      installObserver();
    }
  }

  function updateDateInputLang(root) {
    const htmlLang = SUPPORTED_LANGUAGES[currentLanguage]?.htmlLang || "pt-BR";
    const target = root && typeof root.querySelectorAll === "function" ? root : document;
    target.querySelectorAll('input[type="date"], input[type="datetime-local"]').forEach((inp) => {
      inp.lang = htmlLang;
    });
  }

  function setLanguage(language) {
    saveLanguage(language);
    setDocumentLanguage();
    updateDateInputLang();
    withObserverPaused(() => translateTree(document.body));
    applyFlatpickr();
    document.dispatchEvent(new CustomEvent("monitora:languagechange", {
      detail: { language: currentLanguage, locale: getLocale() }
    }));
  }

  function parseNumber(value) {
    if (typeof value === "number") return Number.isFinite(value) ? value : null;
    let text = String(value || "").trim();
    if (!text) return null;

    text = text.replace(/[^\d,.-]/g, "");
    const lastComma = text.lastIndexOf(",");
    const lastDot = text.lastIndexOf(".");
    const decimalIndex = Math.max(lastComma, lastDot);

    if (decimalIndex >= 0) {
      const integer = text.slice(0, decimalIndex).replace(/[^\d-]/g, "");
      const decimal = text.slice(decimalIndex + 1).replace(/\D/g, "");
      text = `${integer || "0"}.${decimal}`;
    } else {
      text = text.replace(/[^\d-]/g, "");
    }

    const number = Number(text);
    return Number.isFinite(number) ? number : null;
  }

  function formatNumber(value, options = {}) {
    const number = parseNumber(value);
    if (number === null) return "";

    const formatter = new Intl.NumberFormat(getLocale(), {
      minimumFractionDigits: options.minimumFractionDigits ?? 0,
      maximumFractionDigits: options.maximumFractionDigits ?? 2,
      useGrouping: options.useGrouping ?? false
    });
    return formatter.format(number);
  }

  function formatGrade(value) {
    return formatNumber(value, { maximumFractionDigits: 2, useGrouping: false });
  }

  function formatMoney(value) {
    const number = parseNumber(value);
    if (number === null) return "";
    return `R$ ${formatNumber(number, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }

  function decimalSeparator() {
    return currentLanguage === "en" ? "." : ",";
  }

  function normalizeDecimalInput(value) {
    const number = parseNumber(value);
    if (number === null) return "";
    return number.toFixed(2).replace(".", decimalSeparator());
  }

  function parseDate(value) {
    if (!value) return null;
    if (value instanceof Date) return Number.isNaN(value.getTime()) ? null : value;

    const text = String(value).trim();
    const isoDateTime = text.match(/^(\d{4})-(\d{2})-(\d{2})(?:[T\s](\d{2}):(\d{2})(?::(\d{2}))?)?/);
    if (isoDateTime) {
      const [, y, m, d, hh = "0", mm = "0", ss = "0"] = isoDateTime;
      const date = new Date(Number(y), Number(m) - 1, Number(d), Number(hh), Number(mm), Number(ss));
      return Number.isNaN(date.getTime()) ? null : date;
    }

    const localized = text.match(/^(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})(?:\s+(\d{1,2}):(\d{2}))?$/);
    if (localized) {
      let [, a, b, y, hh = "0", mm = "0"] = localized;
      if (y.length === 2) y = `20${y}`;
      const month = currentLanguage === "en" ? Number(a) : Number(b);
      const day = currentLanguage === "en" ? Number(b) : Number(a);
      const date = new Date(Number(y), month - 1, day, Number(hh), Number(mm));
      return Number.isNaN(date.getTime()) ? null : date;
    }

    const date = new Date(text);
    return Number.isNaN(date.getTime()) ? null : date;
  }

  function formatDate(value, options = {}) {
    const date = parseDate(value);
    if (!date) return "";
    const defaultOptions = { day: "2-digit", month: "2-digit", year: "numeric" };
    return new Intl.DateTimeFormat(
      getLocale(),
      Object.keys(options).length ? options : defaultOptions
    ).format(date);
  }

  function formatTime(value, options = {}) {
    const date = parseDate(value);
    if (!date) return "";
    return new Intl.DateTimeFormat(getLocale(), {
      hour: "2-digit",
      minute: "2-digit",
      ...options
    }).format(date);
  }

  function formatDateTime(value, options = {}) {
    const date = parseDate(value);
    if (!date) return "";
    return new Intl.DateTimeFormat(getLocale(), {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      ...options
    }).format(date);
  }

  function monthName(index, width = "long") {
    const date = new Date(2026, Number(index) || 0, 1);
    return new Intl.DateTimeFormat(getLocale(), { month: width }).format(date);
  }

  function weekdayNames(width = "short") {
    const base = new Date(2026, 5, 8); // Monday
    return Array.from({ length: 7 }, (_, index) => {
      const date = new Date(base);
      date.setDate(base.getDate() + index);
      return new Intl.DateTimeFormat(getLocale(), { weekday: width }).format(date).replace(".", "").toUpperCase();
    });
  }

  function installSwalWrapper() {
    if (!window.Swal || window.Swal.__monitoraI18nWrapped) return;
    const originalFire = window.Swal.fire.bind(window.Swal);
    const originalValidation = typeof window.Swal.showValidationMessage === "function"
      ? window.Swal.showValidationMessage.bind(window.Swal)
      : null;
    const translatedFire = function (...args) {
      const nextArgs = args.map((arg, index) => {
        if (typeof arg === "string") return translate(arg);
        if (!arg || typeof arg !== "object" || index > 0) return arg;
        const copy = { ...arg };
        ["title", "titleText", "text", "confirmButtonText", "cancelButtonText", "denyButtonText", "inputPlaceholder", "inputLabel", "footer"].forEach((key) => {
          if (typeof copy[key] === "string") copy[key] = translate(copy[key]);
        });
        if (typeof copy.html === "string") copy.html = translateHtmlFragment(copy.html);
        return copy;
      });
      return originalFire(...nextArgs).then((result) => {
        translateTree(document.body);
        return result;
      });
    };
    Object.assign(translatedFire, window.Swal.fire);
    window.Swal.fire = translatedFire;
    if (originalValidation) {
      window.Swal.showValidationMessage = function (message) {
        return originalValidation(translateHtmlFragment(message));
      };
    }
    window.Swal.__monitoraI18nWrapped = true;
  }

  function buildFlatpickrOpts(el) {
    const isDatetime = el.type === "datetime-local";
    const lang = currentLanguage;
    let locale = null;
    if (lang === "pt" && typeof flatpickr !== "undefined" && flatpickr.l10ns && flatpickr.l10ns.pt) {
      locale = flatpickr.l10ns.pt;
    } else if (lang === "es" && typeof flatpickr !== "undefined" && flatpickr.l10ns && flatpickr.l10ns.es) {
      locale = flatpickr.l10ns.es;
    }
    const isEN = lang === "en";
    const placeholder = isDatetime
      ? (isEN ? "MM/DD/YYYY HH:MM" : "DD/MM/AAAA HH:MM")
      : (isEN ? "MM/DD/YYYY" : "DD/MM/AAAA");
    return {
      locale: locale,
      altInput: true,
      altFormat: isDatetime ? (isEN ? "m/d/Y H:i" : "d/m/Y H:i") : (isEN ? "m/d/Y" : "d/m/Y"),
      dateFormat: isDatetime ? "Y-m-d\\TH:i" : "Y-m-d",
      enableTime: isDatetime,
      time_24hr: true,
      allowInput: false,
      disableMobile: true,
      onReady: function (_, __, fp) {
        if (fp.altInput) fp.altInput.placeholder = placeholder;
      }
    };
  }

  function applyFlatpickr() {
    if (typeof flatpickr === "undefined") return;
    document.querySelectorAll('input[type="date"], input[type="datetime-local"]').forEach(function (el) {
      const opts = buildFlatpickrOpts(el);
      if (el._flatpickr) {
        const saved = el._flatpickr.selectedDates.slice();
        el._flatpickr.destroy();
        const fp = flatpickr(el, opts);
        if (saved.length) fp.setDate(saved[0], false);
      } else {
        flatpickr(el, opts);
      }
    });
  }

  function setFlatpickrDate(el, isoValue) {
    if (!el) return;
    if (el._flatpickr) {
      el._flatpickr.setDate(isoValue || null, false);
    } else {
      el.value = isoValue || "";
    }
  }

  function init() {
    setDocumentLanguage();
    installStyles();
    ensureLanguageControl();
    translateTree(document.body);
    updateDateInputLang();
    installObserver();
    installSwalWrapper();
    setInterval(installSwalWrapper, 500);
    setTimeout(applyFlatpickr, 0);
  }

  window.MonitoraI18n = {
    languages: SUPPORTED_LANGUAGES,
    getLanguage,
    getLocale,
    setLanguage,
    t: translate,
    translate,
    translatePage: translateTree,
    parseNumber,
    formatNumber,
    formatGrade,
    formatMoney,
    normalizeDecimalInput,
    parseDate,
    formatDate,
    formatTime,
    formatDateTime,
    monthName,
    weekdayNames,
    applyFlatpickr,
    setDate: setFlatpickrDate
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
