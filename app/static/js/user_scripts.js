$(function ()
{
    /* Fonctions */
    /* --------- */

    let modify_user_profile = function()
    {
        let btn = $(this);

        window.location.href = btn.attr("data-url");
    }

    /* Liens */
    /* ----- */

    $("#modify-user-profile").click(modify_user_profile);
});
