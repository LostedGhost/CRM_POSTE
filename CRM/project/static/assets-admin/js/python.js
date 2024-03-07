function toUser(name){
  var dict = {
    "intitule":"intitulé",
    "name": "nom",
    "site": "ville",
    "login": "login",
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
  for (var i = 0; i < form.elements.length; i++) {
    var element = form.elements[i];
    if (element.type !== "submit" && element.name !== "csrfmiddlewaretoken") {
      if (element.tagName === "SELECT") {
        var selectedIndex = element.selectedIndex;
        if (selectedIndex !== -1) {
          value = element.options[selectedIndex].text;
        }
      }
      else{
        value = element.value;
      }
      recap += "<strong class='text-uppercase'> " + toUser(element.name) + " :</strong> " + value + "</p><br><p>";
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