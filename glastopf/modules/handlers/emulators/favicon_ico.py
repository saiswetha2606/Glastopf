# Copyright (C) 2015 Lukas Rist
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from glastopf.modules.handlers import base_emulator
import os


class FaviconHandler(base_emulator.BaseEmulator):
    def __init__(self, data_dir):
        super(FaviconHandler, self).__init__(data_dir)

    def handle(self, attack_event):
        with open(os.path.join(self.data_dir, 'favicon/favicon.ico'), 'r') as favicon:
            data = favicon.read()
            attack_event.http_request.set_response(data, headers=(('Content-Type, image/x-icon'),))
