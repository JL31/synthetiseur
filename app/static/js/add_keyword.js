$(function ()
{
    /* Fonctions */
    /* --------- */

    /* Function that handles the addition of a keyword, for the specified article, into the database */
    let keyword_addition_request = function()
    {
        let form = $("#create-article-form");

        $.ajax(
        {
            url: form.attr("action"),
            type: form.attr("method"),
            data: form.serialize(),
            dataType: 'json',
            success: function(data)
            {
                if (data.already_exists)
                {
                    alert("Ce mot clé existe déjà !");
                }

                $("#keywords").val("");
            }
        });
    };

    /* Function that handles the addition of a keyword for an article */
    let addKeyword = function(event)
    {
        if (event.keyCode == 13)    // 13 stands for the "Enter" key
        {
            event.preventDefault();

            keyword_addition_request();
        }
        
    };

    /* Links */
    /* ----- */

    $("#keywords").keydown(addKeyword);
});
