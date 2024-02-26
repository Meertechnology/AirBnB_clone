#!/usr/bin/python3
"""Defines the HBnB console."""
import cmd
import re
from shlex import split
from models import storage
from models.base_model import BaseModel
from models.user import User
from models.state import State
from models.city import City
from models.place import Place
from models.amenity import Amenity
from models.review import Review


def parse(arg):
    curl_braces = re.search(r"\{(.*?)\}", arg)
    bracket = re.search(r"\[(.*?)\]", arg)
    if curl_braces is None:
        if bracket is None:
            return [x.strip(",") for x in split(arg)]
        else:
            tknize = split(arg[:bracket.span()[0]])
            ret_list = [x.strip(",") for x in tknize]
            ret_list.append(brackets.group())
            return ret_list
    else:
        tknize = split(arg[:curl_braces.span()[0]])
        ret_list = [i.strip(",") for i in tknize]
        ret_list.append(curl_braces.group())
        return ret_list


class HBNBCommand(cmd.Cmd):
    """Defines the HolbertonBnB(hbnb) command interpreter.
    Attributes:
        prompt (str): The command prompt.
    """

    prompt = "(hbnb) "
    __classes = {
        "BaseModel",
        "User",
        "State",
        "City",
        "Place",
        "Amenity",
        "Review"
    }

    def emptyline(self):
        """Do nothing upon receiving an empty line."""
        pass

    def default(self, arg):
        """Defaults behavior for cmd module when input is invalid"""
        argDict = {
            "all": self.do_all,
            "show": self.do_show,
            "destroy": self.do_destroy,
            "count": self.do_count,
            "update": self.do_update
        }
        match = re.search(r"\.", arg)
        if match is not None:
            arg_list = [arg[:match.span()[0]], arg[match.span()[1]:]]
            match = re.search(r"\((.*?)\)", arg_list[1])
            if match is not None:
                command = [arg_list[1][:match.span()[0]], match.group()[1:-1]]
                if command[0] in argDict.keys():
                    call = "{} {}".format(arg_list[0], command[1])
                    return argDict[command[0]](call)
        print("*** Unknown syntax: {}".format(arg))
        return False

    def do_quit(self, arg):
        """Quit command to exit the program."""
        return True

    def do_EOF(self, arg):
        """EOF signal to exit the program."""
        print("")
        return True

    def do_create(self, arg):
        """Usage: create <class>
        Creates a new class instance and print its id.
        """
        arg_list = parse(arg)
        if len(arg_list) == 0:
            print("** class name missing **")
        elif arg_list[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        else:
            print(eval(arg_list[0])().id)
            storage.save()

    def do_show(self, arg):
        """Usage: show <class> <id> or <class>.show(<id>)
        Display string representation of a class instance of a given id.
        """
        arg_list = parse(arg)
        objDict = storage.all()
        if len(arg_list) == 0:
            print("** class name missing **")
        elif arg_list[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        elif len(arg_list) == 1:
            print("** instance id missing **")
        elif "{}.{}".format(arg_list[0], arg_list[1]) not in objDict:
            print("** no instance found **")
        else:
            print(objDict["{}.{}".format(arg_list[0], arg_list[1])])

    def do_destroy(self, arg):
        """Usage: destroy <class> <id> or <class>.destroy(<id>)
        Delete a class instance of a given id."""
        arg_list = parse(arg)
        objDict = storage.all()
        if len(arg_list) == 0:
            print("** class name missing **")
        elif arg_list[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        elif len(arg_list) == 1:
            print("** instance id missing **")
        elif "{}.{}".format(arg_list[0], arg_list[1]) not in objDict.keys():
            print("** no instance found **")
        else:
            del objDict["{}.{}".format(arg_list[0], arg_list[1])]
            storage.save()

    def do_all(self, arg):
        """Usage: all or all <class> or <class>.all()
        Display string representations of all instances of a given class.
        If no class is specified, displays all instantiated objects."""
        argList = parse(arg)
        if len(argList) > 0 and argList[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        else:
            obj_list = []
            for obj in storage.all().values():
                if len(argList) > 0 and argList[0] == obj.__class__.__name__:
                    obj_list.append(obj.__str__())
                elif len(argList) == 0:
                    obj_list.append(obj.__str__())
            print(obj_list)

    def do_count(self, arg):
        """Usage: count <class> or <class>.count()
        Retrieve the number of instances of a given class."""
        argList = parse(arg)
        counter = 0
        for obj in storage.all().values():
            if argList[0] == obj.__class__.__name__:
                counter += 1
        print(counter)

    def do_update(self, arg):
        """Usage: update <class> <id> <attribute_name> <attribute_value> or
       <class>.update(<id>, <attribute_name>, <attribute_value>) or
       <class>.update(<id>, <dictionary>)
        Update a class instance of a given id by adding or updating
        a given attribute key/value pair or dictionary."""
        argList = parse(arg)
        objDict = storage.all()

        if len(argList) == 0:
            print("** class name missing **")
            return False
        if argList[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
            return False
        if len(argList) == 1:
            print("** instance id missing **")
            return False
        if "{}.{}".format(argList[0], argList[1]) not in objDict.keys():
            print("** no instance found **")
            return False
        if len(argList) == 2:
            print("** attribute name missing **")
            return False
        if len(argList) == 3:
            try:
                type(eval(argList[2])) != dict
            except NameError:
                print("** value missing **")
                return False

        if len(argList) == 4:
            obj = objDict["{}.{}".format(argList[0], argList[1])]
            if argList[2] in obj.__class__.__dict__.keys():
                val_type = type(obj.__class__.__dict__[argList[2]])
                obj.__dict__[argList[2]] = val_type(argList[3])
            else:
                obj.__dict__[argList[2]] = argList[3]
        elif type(eval(argList[2])) == dict:
            obj = objDict["{}.{}".format(argList[0], argList[1])]
            for k, val in eval(argList[2]).items():
                if (k in obj.__class__.__dict__.keys() and
                        type(obj.__class__.__dict__[k]) in {str, int, float}):
                    val_type = type(obj.__class__.__dict__[k])
                    obj.__dict__[k] = val_type(val)
                else:
                    obj.__dict__[k] = val
        storage.save()


if __name__ == "__main__":
    HBNBCommand().cmdloop()
