import ReflectionAPI from "../lib/reflection-api.mjs";
import fs from 'fs'


class Endpoint extends ReflectionAPI {
    /**
     * Check a Checkbox
     * @param int id The id of the checkbox.
     * @return mixed int(7) on success, null or false on failure.
     */
    check(id) {
        if (!isInteger(id)) return null;
        return fs.writeFileSync(`Checkbox-${id}.txt`, "checked");
    }

    /**
     * Uncheck a Checkbox
     * @param int id The id of the checkbox.
     * @return mixed true on success, false or null on failure.
     */
    uncheck(id) {
        if (!isInteger(id)) return null;
        if (!fs.fs.existsSync(`Checkbox-${id}.txt`)) return false;
        return fs.unlinkSync(`Checkbox-${id}.txt`);
    }

    /**
     * See if a checkbox is checked or not.
     * @param int id The id of the checkbox.
     * @return bool True if the checkbox is checked, 
     * false if not or if it doesn't even exist.
     */
    checked(id) {
        return fs.existsSync(`Checkbox-${id}.txt`);
    }
}

var x = new Endpoint();

console.log(x._functions);