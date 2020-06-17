$(function ()
{
    /* Fonctions */
    /* --------- */

    /* Function that handles the addition of a reference, for the specified article, into the database */
    let reference_addition_request = function()
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
                references_retrieval_request(data);

                $("#references").val("");
            }
        });
    };

    /* Function that handles the retrieval of the several references to update the page */
    let references_retrieval_request = function(data)
    {
        $("#references-container").html(data.html_form);
    };

    /* Function that handles the addition of a reference for an article */
    let addReference = function(event)
    {
        if (event.keyCode == 13)    // 13 stands for the "Enter" key
        {
            event.preventDefault();

            reference_addition_request();
        }
        
    };

    /* Function that deletes the clicked button */
    let deleteReference = function()
    {
        let btn = $(this);

        $.ajax(
        {
            url: btn.attr("data-url"),
            success: function(data)
            {
                references_retrieval_request(data);
            }
        });
    };

    /* Links */
    /* ----- */

    $("#references").keydown(addReference);
    $("#references-container").on("click", ".btn-warning", deleteReference);
});
