$(function ()
{
    /* Fonctions */
    /* --------- */

    /* Function that handles the request to check for an article title */
    let check_title_request = function()
    {
        let form = $("#create-article-form");
        let title_field = $("#title-field");

        $.ajax(
        {
            url: title_field.attr("data-url"),
            type: form.attr("method"),
            data: form.serialize(),
            dataType: 'json',
            success: function(data)
            {
                if (data.title_already_exists)
                {
                    alert("Ce titre est déjà pris, merci d'en choisir un autre");
                    $("#title").val("");
                }
            }
        });
    };

    /* Links */
    /* ----- */

    $("#title").focusout(check_title_request);
});
