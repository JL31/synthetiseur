$(function ()
{
    /* Fonctions */
    /* --------- */

    let modify_article = function()
    {
        let btn = $(this);

        window.location.href = btn.attr("data-url");
    }

    let confirm_article_deletion_modal_loading = function()
    {
        let btn = $(this);

        $.ajax(
        {
            url: btn.attr("data-url"),
            type: 'get',
            dataType: 'json',
            beforeSend: function ()
            {
                $("#modal-article").modal("show");
            },
            success: function (data)
            {
                $("#modal-article .modal-content").html(data.html_form);
            }
        });
    };

    let delete_article = function()
    {
        let form = $(this);

        $.ajax(
        {
            url: form.attr("action"),
            type: form.attr("method"),
            data: donnees,
            processData: false,
            contentType: false,
            dataType: 'json',
            success: function ()
            {}
        });

        return false;

    };

    /* Liens */
    /* ----- */

    $("#modify-article").click(modify_article);
    $("#delete-article").click(confirm_article_deletion_modal_loading);

    $("#modal-article").on("submit", delete_article);
});
