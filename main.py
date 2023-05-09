import fire

import GoogleDrive


def check_files():
    '''
    Returns a greeting message
    Parameters
    ----------
    name : string
        String that represents the addresses name

    Returns
    -------
    string
        greeting message concatenated with name
    '''
    files = GoogleDrive.search_files()


if __name__ == '__main__':
    fire.Fire()
