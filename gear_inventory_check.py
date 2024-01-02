#!/usr/bin/env python3
"""Check level of gear inventory and send an email showing changes between days

Usage:

License:
    BSD Clause 3 License

    Copyright (c) 2022, Fredrick W. Warren
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice, this
      list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.

    * Neither the name of the copyright holder nor the names of its
      contributors may be used to endorse or promote products derived from
      this software without specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
    FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
    DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
    CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
    OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import sys
import os
import click
import json
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from envelopes import Envelope
from smtplib import SMTPException # allow for silent fail in try exception

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """

    try:
        base_path = sys._MEIPASS  # pylint: disable=protected-access
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def split_address(email_address):
    """Return a tuple of (address, name), name may be an empty string
       Can convert the following forms
         exaple@example.com
         <example@exmaple.con>
         Example <example@example.com>
         Example<example@example.com>
    """
    address = email_address.split('<')
    if len(address) == 1:
        return (address[0], '')
    if address[0]:
        return (address[1][:-1], address[0].strip())
    return (address[1][:-1], '')

def mail_results(subject, body):
    """ Send emial with html formatted body and parameters from env"""
    envelope = Envelope(
        from_addr=split_address(os.environ.get('MAIL_FROM')),
        subject=subject,
        html_body=body
    )

def email_admins(low, status):
    """eamil admins about cartridge status"""
    subject = "Need to reorder ink for plotter"
    body = f"""
        <p>Time to order some more of the following inkjet ink</p>
        <pre>{low}</pre>
        <br />
        <p>These are the overall cartridge levels</p>
        <pre>{status}</pre>
    """
    mail_results(subject, body)

def email_status(low, status):  # pylint: disable=unused-argument
    """eamil admins about cartridge status"""
    subject = "HP Z5200 Plotter Ink Cartridge Status Report"
    body = f"""
        <p>These are the overall cartridge levels</p>
        <pre>{status}</pre>
				<p>For more details please click <a href="http://10.10.200.130/">here</a>.</p>
    """
    mail_results(subject, body)



def format_list(cartridges):
    """format cartridge list"""

    text  = ""
    for row in cartridges:
        line = (f"    {row['cartridge']:20}  "
                f"{'(' + row['letter'] + ')':4}  "
                f"{row['part']}  "
                f"{row['level']:>5}  "
                f"{row['status']}\n")
        text += line
    return text


# pylint: disable=no-value-for-parameter
@click.command()
@click.option('--debug', '-d', is_flag=True,
    help='show debug output do not email')
@click.option('--status', '-s', is_flag=True,
    help='just print/show status')
def main(debug, status):
    """check ink levels and email results"""

    # load environmental variables
    load_dotenv(dotenv_path=resource_path(".env"))
    if debug:
        print("Cartridge Status")
        return


if __name__ == "__main__":
    main()

# vim: ts=4 sw=4 et
