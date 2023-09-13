    
    //General Page
    const allowedExtensionsFile = ["pdf", "json", "txt", "docx", "cpp", "xlsx", "csv", "html", "py", "java", "xls"] 
    const allowedExtensionsAudio = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]
    waiting_chat = false // Indica se c'e' una richiesta in corso nella schermata chat
    waiting_chat_traslate = false // Indica se c'e' una richiesta in corso nella schermata translate
    waiting_audio = false // Indica se c'e' una richiesta in corso nella schermata audio
    translate = false // Indica se siamo nella schermata di traduzione
    side_bar = false // Indica se la side bar e' attiva
    audio = false // Indica se siamo nella schermata di audio
    cluster = true // Indica se siamo nella schermata di clustering
    side_bar_id = "chat_sidebar" // Memorizza l'id dell'ultima sidebar attiva
    lang_option = false // Indica se il menu delle lingue e' visualizzato o meno
    audio_badge = false // Visualizzazzione del badge di notifica
    form_text_val = "" // Contiene il contenuto della richiesta

function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}
    //Verifica e regola la grandezza della interfaccia
function check_sidebar(){
        let side_bar_element = $("#cont");
        if (side_bar) {
        side_bar_element.removeClass("offset-md-3 col-md-8");
        side_bar_element.addClass("offset-md-4 col-md-7");
    } else {
        side_bar_element.removeClass("offset-md-4 col-md-7");
        side_bar_element.addClass("offset-md-3 col-md-8");
    }
    }

    //Show delle sidebar
function show_elements(element) {
    let lastClickedSection = false;

    const config = {
        "chat_sidebar_li": {
            "divId": "chat_sidebar",
            "placeholder": "Inserisci il tuo messaggio o un link ad una pagina web",
            "formTransform": 'none',
            "contextButtonTranform": 'none',

        },
        "translate_sidebar_li": {
            "divId": "translate_sidebar",
            "placeholder": "Inserisci il testo da tradurre",
            "state": "translate",
            "formTransform": 'none',
            "contextButtonTranform": 'translateX(300%)',
        },
        "audio_sidebar_li": {
            "divId": "audio_sidebar",
            "placeholder": "",
            "state": "audio",
            "formTransform": 'translateY(150%)',
            "contextButtonTranform": 'translateX(300%)',
        },
        "cluster_sidebar_li": {
            "divId": "cluster_sidebar",
            "placeholder": "",
            "state": "cluster",
            "contextButtonTranform": 'translateX(300%)',
        },
    };

    const lang_menu = document.getElementById("lang_menu_body");
    const settings = config[element.id];
    let myDiv = document.getElementById(settings.divId);
    let other;

    if (element.id === "chat_sidebar_li") {
        // Se è la chat sidebar, imposta gli altri stati a false
        audio = false;
        translate = false;
    } else {
        // Altrimenti, imposta lo stato specifico
        window[settings.state] = true;
    }



     if (side_bar_id !== settings.divId){
         lastClickedSection = true;
     }

    if (settings.placeholder) {
        document.getElementById('cont_form_text').placeholder = settings.placeholder;
    }

    document.getElementById('cont_form').style.transform = settings.formTransform;
    document.getElementById('button_context').style.transform = settings.contextButtonTranform;



    if (!side_bar) {
        myDiv.style.left = "7rem";
        side_bar = true;
        side_bar_id = settings.divId;
        lang_menu.style.transform = "translateY(400%)";
    } else {
        if (side_bar_id === settings.divId) {
           if(settings.divId == "translate_sidebar"){
               document.getElementById('lang_menu_body').style.transform = "none"
           }
            myDiv.style.left = "-20%";
            side_bar = false;
        } else {
            myDiv.style.left = "7rem";
            other = document.getElementById(side_bar_id);
            other.style.left = "-20%";
            side_bar_id = settings.divId;
        }
    }

    if (audio_badge && side_bar_id === 'audio_sidebar'){
        let alertElement = document.getElementById('audio_badge');
        alertElement.classList.remove('visible');
        audio_badge = false
    }

        // Aggiorno la grandezza della chat in base a se la sidebar e' attiva o meno
        check_sidebar()
        // Richiedo la chat specifica per quell'argomento.
    let formData;
    if (lastClickedSection) {
        formData = new FormData();
        formData.append("sidebar", side_bar_id);

        $.ajax({
            type: "POST",
            url: "/get_elements",
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                update_elements(response)



                if (waiting_audio && side_bar_id === 'audio_sidebar'){
                    showLoadingAnimation()
                }else if(waiting_chat_traslate && side_bar_id === 'translate_sidebar' ){
                    showLoadingAnimation()
                }else if(waiting_chat && side_bar_id === 'chat_sidebar' ){
                    showLoadingAnimation()
                }

            },
            error: function(error){
                alert(error.responseJSON.error);
            },

        });
    }

    }

    // Chiamata Chat
function sendForm() {
        if(waiting_chat || waiting_chat_traslate || $("#cont_form_text").val().replace(/\s/g, '') === ""){
            waiting_alert()
            return
        }



        var formData = new FormData($("#cont_form")[0]);
        formData.append("translate", translate);


        /* Reset dei valori del form*/
        form_text_val = $("#cont_form_text").val()
        showLoadingAnimation()

        $("#cont_form_text").val("")

        document.getElementById('cont_form_text').style.height = 'auto';
        document.getElementById('cont_form_input_file').value = null;    


        if (translate){
            waiting_chat_traslate = true
        }else{
            waiting_chat = true
        }
        $.ajax({
            type: "POST",
            url: "/process_form",
            data: formData,
            processData: false,
            contentType: false,
            success:function(response) {
                    update_elements(response)
                    if (waiting_chat) waiting_chat = false
                    if (waiting_chat_traslate) waiting_chat_traslate = false
                },
            error: function(error) {
                     if (error.responseJSON && error.responseJSON.request_in_progress === true) {
                        waiting_alert();
                    }
                    if(waiting_chat) waiting_chat = false
                    if(waiting_chat_traslate) waiting_chat_traslate = false
                }
            });
        }

    
    /*Text Area Behaviour*/
function switchCont(element) {
        
        if(element.id === "cont_chat"){
            document.getElementById('cont_form_text').style.opacity = '0.5';
            document.getElementById('cont_form_text').style.height = 'auto';
        }else{
            document.getElementById('cont_form_text').style.opacity = '1';
            document.getElementById('cont_form_text').style.height = 'auto';
            document.getElementById('cont_form_text').style.height =  document.getElementById('cont_form_text').scrollHeight + 'px'; 
        }
                      
    }

    /*Model Selection*/
function change_chat_model(element) {
        if(waiting_chat){
            waiting_alert()
            return
        }
        element.classList.add("btn-primary");
        element.classList.remove("bg-transparent");
        if(element.id === "GPT-3" ){
            document.getElementById("GPT-4").classList.add("bg-transparent");
            document.getElementById("GPT-4").classList.remove("btn-primary");
        }else{
           document.getElementById("GPT-3").classList.add("bg-transparent");
           document.getElementById("GPT-3").classList.remove("btn-primary");
        }
            $.ajax({
                type: "POST",
                url: "/model_chat_api",
                data: { new_value: element.value },
            });
        }

    /*Clear Page*/
function clearPage()   {
        if(waiting_chat || waiting_chat_traslate){
            return
        }
        const input = document.getElementById('button_clear_Page');
        input.blur();
        $("#cont_chat").empty()
        $.ajax({
                type: "POST",
                url: "/clear_elements",
                data: {sidebar: side_bar_id},
                error: function(error) {
                    alert(error.responseJSON.error);
                },
            });
        }
 
    /*Upload File Behaviour*/
function upload_file_chat() {
        if(waiting_chat || waiting_chat_traslate){
            waiting_alert()
            return
        }
        
        const input = document.getElementById('cont_form_input_file');
        const childNodes = document.getElementById("cont_contest_file").children;
        const formData = new FormData();

        

        if (!input.files.length) {
            return;
        }
    
        for (var i = 0; i < input.files.length; i++){
            const fileExtension = input.files[0].name.split('.').pop().toLowerCase();
            if (!allowedExtensionsFile.includes(fileExtension)){
                alert("Estensione non consentita")
                return
            }
        }

        for (var i = 0; i < input.files.length; i++) {
            for (var j = 0; j < childNodes.length; j++) {
                    if (childNodes[j].getAttribute('data-filename') === input.files[i].name) {
                        alert("È gia presente un file con questo nome")
                        return
                    }
                    
            }
        }
        
        for (var i = 0; i < input.files.length; i++) {
            formData.append('file[]', input.files[i]);
        }


        document.getElementById('cont_form_text').placeholder="Aspetta la fine del salvataggio dei file nel contesto per scrivere un nuovo messaggio";
        waiting_chat = true
        $.ajax({
                type: "POST",
                url: "/upload_file", 
                data : formData, 
                processData: false,  
                contentType: false, 
                success:function(response) {
                    document.getElementById('cont_form_text').placeholder="Specifica la operazione da eseguire sul file";
                    update_elements(response)
                    waiting_chat = false
                }, 
                error: function(error) {
                    if (error.responseJSON && error.responseJSON.request_in_progress === true) {
                        waiting_alert();
                    }
                    waiting_chat = false;
                    alert(error.responseJSON.error);
                }
            });

        } 

function remFile(element){
        if(waiting_chat){
            return

        }
            $.ajax({
                    type: "POST",
                    url: "/remove_file",
                    data: { file: element},
                    success:function(response) {
                        update_elements(response)
                        childNodes = document.getElementById("cont_contest_file").children;
                        if(childNodes.length < 1){
                            document.getElementById('cont_form_text').placeholder="Inserisci il tuo messaggio o un link ad una pagina web";
                        }
                    },
                    error: function(error) {
                        alert(error.responseJSON.error);
                    }
                });
        }
    //Reset Contest
function resetContest(){
        if(waiting_chat){
            return 
        }
        document.getElementById('cont_form_text').placeholder="Inserisci il tuo messaggio o un link ad una pagina web";
        $("#cont_chat").empty()
        $("#cont_contest_file").empty()
        $("#chat_information_Message").text(0)
        $("#chat_information_Token").text(0)
        $.ajax({
                type: "POST",
                url: "/clear_context",
                error: function(error) {
                    alert(error.responseJSON.error);
                }
            });


    }

    //Elaborazione della risposta
function update_elements(response){

        if (side_bar_id !== response.section ) {
            return
        }


        $("#cont_chat").empty();
        $("#cont_contest_file").empty();


        //Information
        $("#chat_information_Message").text(response.information.Num_Message)
        $("#chat_information_Token").text(response.information.Num_Token)
        
        // File Elements
        for(var i = 0; i < response.file.length; i++){
            var file_contest = response.file[i];
            var file_contest_element = $("<div>")
                .attr("class", "card text-start border-0 p-1 mt-1 mb-1 shadow-lg")
                .attr("data-filename" , file_contest.file)
                .html(
                    "<h3 class='card-title fs-6 fw-bold pe-5 mb-0 custom-fs' id='UploadedFile_Name' data-filename='" + file_contest.file + "'>"+ file_contest.file + "</h3>" +
                    "<p class='card-text mb-0 fs-6 custom-fs' id='UploadedFile_Token' data-filename='" + file_contest.file + "'>Token: "+ file_contest.token + "</p>" +
                    "<button class='btn btn-outline-danger btn-sm ms-auto position-absolute end-0 me-1' " +
                    "data-filename='" + file_contest.file + "'" +
                    " onclick='remFile(" + '"'+ file_contest.file+ '"'+")'><i class='fa-solid fa-square-minus'></i></button>"
                    ); 
                $("#cont_contest_file").append(file_contest_element)                                                   
        }
 
        /* Nel caso di Stampa Inversa */
        // Elements
        response.elements.reverse();
        for (var i = 0; i < response.elements.length; i++) {
            var element = response.elements[i];
            
            if(element.user_text){
                var userText = $("<div>").attr("class" , "row").attr("id", "cont_user_chat").html("<pre> <span class='text-primary'> -> |</span> " + element.user_text + "</pre>");
                $("#cont_chat").append(userText);
            }
            if(element.response_text){
                var aiText = $("<div>").attr("class" ,"row bg-body rounded-3 p-3 shadow mt-2").attr("id", "cont_ai_chat").html("<pre>" + element.response_text + "</pre>");
                $("#cont_chat").append(aiText);
            }
            
            // Controlla se esiste il link_text nell'elemento
            if (element.link_text) {
                var linkText = $("<div>").attr("class" ,"d-flex p-1 shadow rounded-3 mt-4").attr("id", "cont_link_chat").html(element.link_text);
                aiText.append(linkText);
            }
      
        }
    }
            
    
    //Escaping dei Dati
$(document).on('click', '.cont_button_rem_File_label', function() {
       
        var filename = $(this).data('filename');
        var associatedButton = $("button[data-filename='" + filename + "']");
        associatedButton.click();
        
    });


    //LogOut

function LogOut(){
            $.ajax({
                    type: "POST",
                    url: "/LogOut",
                    success: function(response) {
                        window.location.href = "/auth/login";
                    },
                    error: function(error) {
                        alert(error.responseJSON.error);
                    }


                });
        }

    // Appena si carica la pagina
$(document).ready(function() {

        var elemento = document.getElementById('cont_form_text');
        if (elemento) {
            
            elemento.addEventListener('input', function () {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight) + 'px';

                $.ajax({
                    type: "POST",
                    url: "/get_token",  
                    data: {text : this.value},
                    success: function(response) {
                         $("#chat_information_Token_Messaggio").text(response.token)
                    },
                    error: function(error) {
                        alert(error.responseJSON.error);
                    }
                
                });

            });
        }

        var elemento = document.getElementById("cont_form_text");
          
            if (elemento) {
              elemento.addEventListener("keydown", function(event) {
                if (event.keyCode == 13 && !event.shiftKey) {     
                  event.preventDefault(); 
                  sendForm();
                }
              });
            }
     
        $("#cont_form").on("submit", function(event) {
                event.preventDefault();
        }); 
       
        const themeDropdown = document.getElementById('themeDropdown');
        const htmlElement = document.documentElement
        themeDropdown.addEventListener('click', (event) => {
            const selectedTheme = event.target.getAttribute('data-theme');
        
            if (selectedTheme === 'dark') {
                htmlElement.setAttribute('data-bs-theme', 'dark');
                themeIcon.className = 'fa-solid fa-moon';
            } else if (selectedTheme === 'light') {
                themeIcon.className = 'fa-solid fa-sun';
                htmlElement.setAttribute('data-bs-theme', 'light');
            }
        });
        
        $(".nav-link").click(function() {
            $(".nav-link").removeClass("active");
            $(".nav-link").addClass("link-body-emphasis");
            
            $(this).addClass("active"); 
            $(this).removeClass("link-body-emphasis");

        });
        });

 // Lenguage Selection
    function change_trans_model(element) {
        if(waiting_chat_traslate){
            waiting_alert()
            return
        }
        element.classList.add("btn-primary");
        element.classList.remove("bg-transparent");
        if(element.id === "Google-AI" ){
            document.getElementById("GPT-AI").classList.add("bg-transparent");
            document.getElementById("GPT-AI").classList.remove("btn-primary");
        }else{

           // document.getElementById("Google-AI").classList.add("bg-transparent");
           // document.getElementById("Google-AI").classList.remove("btn-primary");
        }




            $.ajax({
                type: "POST",
                url: "/model_trans_api",
                data: { new_value: element.value },
            });
        }

function change_language(element,opt) {
      let button;
         if (opt === 'audio') {
             button = document.getElementById("current_audiolang")
             button.textContent = element.value + " "
         } else {
             // Seleziona tutti gli elementi con la classe "ibutton"
                var ibuttons = document.querySelectorAll('.current_lang');

                // Itera attraverso gli elementi e cambia il testo
                ibuttons.forEach(function(ibutton) {
                  ibutton.textContent = element.value + " "
                });



         $.ajax({
             type: "POST",
             url: "/language_select",
             data: {new_value: element.value},
         });
     }

}


function change_translate_opt(element,opt) {
      let button;
      button = document.getElementById("current_file_opt")
      button.textContent = opt + " "


}

function translate_file() {

    if(waiting_chat || waiting_chat_traslate){
        waiting_alert()
        return
    }


    let input = document.getElementById('translate_file_input');
    const fileExtension = input.files[0].name.split('.').pop().toLowerCase();
    if (!allowedExtensionsFile.includes(fileExtension)){
            alert("Estensione non consentita")
            return
        }
    else if($('#current_file_opt').text().trim().toLowerCase() === 'documento' && fileExtension !== "docx"){
            alert("Estensione non consentita")
            return
    }

    if (!input.files.length) {
        return;
    }
   

    var formData = new FormData();
    formData.append("file", input.files[0]);
    formData.append("opt", $('#current_file_opt').text().trim().toLowerCase());


    showLoadingAnimation()


    waiting_chat_traslate = true
    document.getElementById('cont_form_text').placeholder="Traduzione in corso, attendere...";
    $.ajax({
            type: "POST",
            url: "/translate_file", 
            data : formData,
            processData: false,  
            contentType: false,
            success:function(response) {
                update_elements(response)
                waiting_chat_traslate = false
                document.getElementById('cont_form_text').placeholder="Inserisci il testo da tradurre";
            }, 
            error: function(error) {
                if (error.responseJSON && error.responseJSON.request_in_progress === true) {
                        waiting_alert();
                    }
                waiting_chat_traslate = false;

            }
        });
}

    //Lang Search Selection
function filterLanguages(id) {
        const input = document.getElementById('languageSearch' + id).value.toLowerCase();
        const languageList = document.getElementById('languageList' + id);
        const languages = languageList.getElementsByTagName('li');

        for (let i = 0; i < languages.length; i++) {
            var language = languages[i].textContent.toLowerCase();
            if (language.includes(input)) {
                languages[i].style.display = '';
                console.log(languages[i]);
            } else {
                languages[i].style.display = 'none';
            }
        }
    }

//Audio Page
function change_audioOption(element){
     button = document.getElementById("current_audioOption")

     button.textContent  = element.value + " "

    let lang_menu;
    lang_menu = document.getElementById("audio_lang_menu")
    if (element.value === "Traduzione") {
        lang_menu.style.transform = 'none'
        lang_option = true
    } else if (lang_option) {
        lang_menu.style.transform = 'translateX(-400%)'
        lang_option = false
    }
    }
function transcribe_audio(){
    if(waiting_audio){
        return
    }

    let input = document.getElementById('transcribe_audio_input');
    let selectedOption = $('#current_audioOption').text().trim()

    const fileExtension = input.files[0].name.split('.').pop().toLowerCase();

    if (!input.files.length) {
        return;
    }
   
    if (!allowedExtensionsAudio.includes(fileExtension)){
            alert("Estensione non consentita")
            return
        }

    let formData = new FormData();
    formData.append("file", input.files[0]);
    formData.append("transcriptionOption", selectedOption);
    if(selectedOption === "Traduzione"){
        let selectedLanguage = $("#current_audiolang").text().trim()
        formData.append("translationLanguage", selectedLanguage);
    }



   showLoadingAnimation()

    waiting_audio = true
    $.ajax({
            type: "POST",
            url: "/transcribe_audio", 
            data : formData,
            processData: false,  
            contentType: false,
            xhr: function() {
                    const xhr = new window.XMLHttpRequest();
                    xhr.upload.addEventListener("progress", function(event) {
                        if (event.lengthComputable) {
                            $('#progress_bar_State').text("Caricamento");
                            const percentComplete = (event.loaded / event.total) * 100;
                            $('#progress_bar_audio').css("width" , percentComplete + '%')
                            if (percentComplete >= 100) {
                                $('#progress_bar_State').text("Elaborazione della Richiesta ~3min");
                            }
                        }
                    }, false);
                    return xhr;
                },
            success:function(response) {
                $('#progress_bar_State').text("Nessun Caricamento");
                $('#progress_bar_audio').css("width" , 0 + '%')
                update_elements(response)
                waiting_audio = false
                if(side_bar_id !== 'audio_sidebar'){
                    audio_badge = true
                    let alertElement = document.getElementById('audio_badge');
                    alertElement.classList.add('visible');
                }
            }, 
            error: function(error) {
                 if (error.responseJSON && error.responseJSON.request_in_progress === true) {
                        waiting_alert();
                    }
                waiting_audio= false;
                $('#progress_bar_State').text("Nessun Caricamento");
                $('#progress_bar_audio').css("width" , 0 + '%')
                alert(error.responseJSON.error);
            }
        });

}

function waiting_alert(){
    //document.getElementById('alert_waiting').style.transform = "none"
    let alertElement = document.getElementById('alert_waiting');
    alertElement.classList.add('visible');

    // Rimuovi la classe "visible" dopo 0.5 secondi per far tornare indietro l'elemento
    setTimeout(function() {
        alertElement.classList.remove('visible');
    }, 5000);
}

function showLoadingAnimation(){

        let chat = document.getElementById("cont_chat");
        let loading_element = chat.querySelector("#cont_ai_chat_tmp");

        if (loading_element) {
            return
        }
        /* Nel caso di Stampa Inversa */
        let element = $("#cont_chat").children();
        $("#cont_chat").empty()

        let safeFormTextVal = escapeHtml(form_text_val);

        if (!translate && !audio) {
            let userText = $("<div>").attr("class", "row").attr("id", "cont_user_chat_tmp").html("<pre> <span class='text-primary'> -> | </span>" + safeFormTextVal + "</pre>");
            $("#cont_chat").append(userText);
        }

        let aiText = $("<div>").attr("class", "row bg-body rounded-3 p-3 shadow mt-2").attr("id", "cont_ai_chat_tmp").html("<pre id='span_tmp'> " + " </pre>");

        $("#cont_chat").append(aiText);
        $("#cont_chat").append(element);
}

window.onbeforeunload = function(event) {
    if(waiting_chat || waiting_audio || waiting_chat_traslate ){
        event.returnValue = 'Stai lasciando la pagina prima che una delle tue richieste sia stata completata.';
    }
};