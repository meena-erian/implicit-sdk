<?php

require_once("../../src/reflection-api.php");


class endpoint extends Reflection_API
{
    /**
     * Check a Checkbox
     * @param int $id The id of the checkbox.
     * @return mixed int(7) on success, null or false on failure.
     */
    function check($id)
    {
        if (!is_int($id)) return null;
        return file_put_contents("Checkbox-$id.txt", "checked");
    }

    /**
     * Uncheck a Checkbox
     * @param int $id The id of the checkbox.
     * @return mixed true on success, false or null on failure.
     */
    function uncheck($id)
    {
        if (!is_int($id)) return null;
        if (!file_exists("Checkbox-$id.txt")) return false;
        return unlink("Checkbox-$id.txt");
    }

    /**
     * See if a checkbox is checked or not.
     * @param int $id The id of the checkbox.
     * @return bool True if the checkbox is checked, 
     * false if not or if it doesn't even exist.
     */
    function checked($id)
    {
        return file_exists("Checkbox-$id.txt");
    }
}
new endpoint();
