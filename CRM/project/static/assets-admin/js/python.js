function toUser(name){
  var dict = {
    "intitule":"intitulé",
    "name": "nom",
    "site": "ville",
    "login": "Nom d'utilisateur",
    "nom": "nom",
    "prenom": "prénom",
    "email": "email",
    "telephone": "téléphone",
    "adresse": "adresse",
    "agence": "agence",
    "regeneratePass": "regénération de mot de passe",
    "denomination":"dénomination",
  }
  if (name in dict)
    return dict[name];
  else
    return name;
}

$("#choixRecherche").on("change", function(e) {
  e.preventDefault();
  var forms = ["form1", "form2", "form3", "form4"];
  forms.forEach(form => {
    var formulaire = document.getElementById(form);
    formulaire.setAttribute("hidden", "true");
  });
  var value = $(this).val();
  var selectOption = document.getElementById(value);
  selectOption.removeAttribute("hidden");
});

$("#choixDomaineStat").on("change", function(e){
  e.preventDefault();
  var forms = ["form1", "form2", "form3"]
  forms.forEach(form => {
    var formulaire = document.getElementById(form);
    formulaire.setAttribute("hidden", "true");
  });
  var value = $(this).val();
  var selectOption = document.getElementById(value);
  selectOption.removeAttribute("hidden");
});

  $("#choixValid").on("change", function(e){
    e.preventDefault();
    var forms = ["form1", "form2"]
    forms.forEach(form => {
      var formulaire = document.getElementById(form);
      formulaire.setAttribute("hidden", "true");
    });
  var value = $(this).val();
  var selectOption = document.getElementById(value);
  selectOption.removeAttribute("hidden");
})


$("#enregistrer").on("click", function(e){
  e.preventDefault();
  var form = document.getElementById('form');
  var recap = "<p>";
  var toAdd = "";
  for (var i = 0; i < form.elements.length; i++) {
    var element = form.elements[i];
    if (element.type !== "submit" && element.name !== "csrfmiddlewaretoken") {
      if (element.tagName === "SELECT") {
        var selectedIndex = element.selectedIndex;
        if (selectedIndex !== -1) {
          value = element.options[selectedIndex].text;
          if (element.hasAttribute('data-name'))
            recap += "<strong class='text-uppercase'> " + toUser(element.getAttribute('data-name')) + " :</strong> " + value + "</p><br><p>";
          else
            recap += "<strong class='text-uppercase'> " + toUser(element.name) + " :</strong> " + value + "</p><br><p>";
        }
      }
      else if (element.type === "radio") {
        if (element.checked) {
          value = element.value;
          recap += "<strong class='text-uppercase'> " + toUser(element.name) + " :</strong> <span class='text-uppercase'>" + toUser(element.getAttribute('data-name')) + "</span> </p><br><p>";
        } else {
          continue; // Skip to next iteration if radio button is not checked
        }
      }
      else{
        value = element.value;
        if (element.hasAttribute('data-name'))
          recap += "<strong class='text-uppercase'> " + toUser(element.getAttribute('data-name')) + " :</strong> " + value + "</p><br><p>";
        else
          recap += "<strong class='text-uppercase'> " + toUser(element.name) + " :</strong> " + value + "</p><br><p>";
      }
      
    }
  }
  recap += "</p>";
  document.getElementById("recap").innerHTML = recap;
  $("#confirmModal").modal("show");
});

$("#valider").on("click", function(e){
  var form = document.getElementById('form');
  form.submit();
});

var debut = $("#debut");
var fin = $("#fin");
var today = new Date().toISOString().split('T')[0];
debut.attr("max", today);

$("#debut").on("change", function(e){
  var today = new Date().toISOString().split('T')[0];
  fin.attr("min", debut.val());
  fin.attr("max", today);
  fin.removeAttr("readonly");
});

var debut1 = $("#debut1");
var fin1 = $("#fin1");
var today1 = new Date().toISOString().split('T')[0];
debut1.attr("max", today1);

$("#debut1").on("change", function(e){
  var today1 = new Date().toISOString().split('T')[0];
  fin1.attr("min", debut1.val());
  fin1.attr("max", today1);
  fin1.removeAttr("readonly");
});



var heureRedirection = 18;
var minuteRedirection = 0;
function redirectAtTime(url, targetHour, targetMinute) {
  // Récupère l'heure actuelle
  const currentTime = new Date();
  const currentHour = currentTime.getHours();
  const currentMinute = currentTime.getMinutes();

  // Convertit l'heure cible en minutes
  const targetTimeInMinutes = targetHour * 60 + targetMinute;
  // Convertit l'heure actuelle en minutes
  const currentTimeInMinutes = currentHour * 60 + currentMinute;

  // Calcule la différence de temps entre l'heure actuelle et l'heure cible
  const timeDifference = targetTimeInMinutes - currentTimeInMinutes;

  // Vérifie si l'heure cible est déjà passée aujourd'hui
  /*if (timeDifference == 0) {
    if (window.location.href != url)
      window.location.href = url;
  } */
  // location.reload();
  if (timeDifference <= 0) {
    // L'heure cible est déjà passée aujourd'hui, redirige immédiatement
    if (window.location.href != url){
      window.location.href = url;
    }
  }
  
}
