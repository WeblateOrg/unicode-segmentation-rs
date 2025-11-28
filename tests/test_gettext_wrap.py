# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: MIT

"""Unit tests for gettext wrapping"""

import unicode_segmentation_rs


class TestGettextWrap:
    """Tests for gettext PO file wrapping"""

    def test_simple_wrap(self):
        text = "This is a simple test string"
        result = unicode_segmentation_rs.gettext_wrap(text, 20)
        assert result == ["This is a simple ", "test string"]

    def test_wrap_with_cjk(self):
        text = "Hello 世界 this is a test"
        result = unicode_segmentation_rs.gettext_wrap(text, 10)
        assert result == ["Hello 世", "界 this ", "is a test"]

    def test_wrap_short_text(self):
        text = "Short"
        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == ["Short"]

    def test_wrap_empty_string(self):
        result = unicode_segmentation_rs.gettext_wrap("", 77)
        assert result == []

    def test_wrap_zero_width(self):
        text = "Test"
        result = unicode_segmentation_rs.gettext_wrap(text, 0)
        assert result == ["Test"]

    def test_wrap_with_punctuation(self):
        text = "Hello, world! How are you?"
        result = unicode_segmentation_rs.gettext_wrap(text, 15)
        assert result == ["Hello, world! ", "How are you?"]

    def test_wrap_with_escape_sequences(self):
        # Escape sequences should not be broken
        text = "This has \\n escape sequences \\t in it"
        result = unicode_segmentation_rs.gettext_wrap(text, 11)
        assert result == ["This has \\n", " escape ", "sequences ", "\\t in it"]

    def test_wrap_long_word(self):
        # Long words that don't fit should still be included
        text = "Supercalifragilisticexpialidocious"
        result = unicode_segmentation_rs.gettext_wrap(text, 20)
        assert result == [text]

    def test_wrap_default_width(self):
        # Test with typical PO file width (77 characters)
        text = "This is a longer sentence that should wrap appropriately at the standard gettext width of seventy-seven characters"
        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == [
            "This is a longer sentence that should wrap appropriately at the standard ",
            "gettext width of seventy-seven characters",
        ]

    def test_wrapping_spaces(self):
        """This tests that we wrap like gettext."""
        text = r"bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345"
        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == [text]

    def test_wrapping_long_fit(self):
        text = r"bla\t12345 12345 12345 12345 12345 12 12345 12345 12345 12345 12345 12345 123"
        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == [text]

    def test_wrapping_long_overflow(self):
        text = r"bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 1"
        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == [
            r"bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 ",
            "1",
        ]

    def test_wrapping_long_multiline_1(self):
        text = "bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 1234\n1234"
        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == [
            "bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 1234\n",
            "1234",
        ]

    def test_wrapping_long_multiline_2(self):
        text = r"bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345\n12345"
        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == [
            r"bla\t12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 12345 ",
            r"12345\n",
            "12345",
        ]

    def test_wrapping_long_escapes(self):
        text = r"\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\"
        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == [
            r"\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\",
            r"\\",
        ]

    def test_wrapping_cjk(self):
        text = "効率的なバグの報告はPostGISの開発を助ける本質的な方法です。最も効率的なバグ報告は、PostGIS開発者がそれを再現できるようにすることで、それの引き金となったス"
        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == [
            "効率的なバグの報告はPostGISの開発を助ける本質的な方法です。最も効率的なバグ報",
            "告は、PostGIS開発者がそれを再現できるようにすることで、それの引き金となったス",
        ]

    def test_wrap_emoji(self):
        text = 'print(ts.string_get_word_breaks("Test ❤️‍🔥 Test")) # Prints [1, 2, 3, 4, 5, '
        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == [text]

    def test_wrap_parenthesis_1(self):
        text = r"Konvertiert [param what] in [param type] auf die bestmögliche Weise. Der [param type] verwendet die [enum Variant.Type]-Werte.\n"
        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == [
            "Konvertiert [param what] in [param type] auf die bestmögliche Weise. Der ",
            r"[param type] verwendet die [enum Variant.Type]-Werte.\n",
        ]

    def test_wrap_parenthesis_2(self):
        text = r"- Eine von [Object] abgeleitete Klasse, die in [ClassDB] existiert, z. B. [Node].\n"
        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == [
            "- Eine von [Object] abgeleitete Klasse, die in [ClassDB] existiert, z. B. ",
            r"[Node].\n",
        ]

    def test_wrap_escape_line(self):
        text = r"%{src?%{dest?转发:入站}:出站} %{ipv6?%{ipv4?<var>IPv4</var> and <var>IPv6</var>:<var>IPv6</var>}:<var>IPv4</var>}%{proto?, 协议 %{proto#%{next?, }%{item.types?<var class=\"cbi-tooltip-container\">%{item.name}<span class=\"cbi-tooltip\">具有类型 %{item.types#%{next?, }<var>%{item}</var>} 的 ICMP</span></var>:<var>%{item.name}</var>}}}%{mark?, 标记 <var%{mark.inv? data-tooltip=\"匹配除 %{mark.num}%{mark.mask? 带有掩码 %{mark.mask}} 的 fwmarks。\":%{mark.mask? data-tooltip=\"在比较前对fwmark 应用掩码 %{mark.mask} 。\"}}>%{mark.val}</var>}%{dscp?, DSCP %{dscp.inv?<var data-tooltip=\"匹配除 %{dscp.num?:%{dscp.name}} 以外的 DSCP 类型。\">%{dscp.val}</var>:<var>%{dscp.val}</var>}}%{helper?, 助手 %{helper.inv?<var data-tooltip=\"匹配除 &quot;%{helper.name}&quot; 以外的任意助手。\">%{helper.val}</var>:<var data-tooltip=\"%{helper.name}\">%{helper.val}</var>}}"

        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == [
            "%{src?%{dest?转发:入站}:出站} %{ipv6?%{ipv4?<var>IPv4</var> and <var>IPv6</",
            "var>:<var>IPv6</var>}:<var>IPv4</var>}%{proto?, 协议 %{proto#%{next?, }%",
            r"{item.types?<var class=\"cbi-tooltip-container\">%{item.name}<span ",
            r"class=\"cbi-tooltip\">具有类型 %{item.types#%{next?, }<var>%{item}</var>} 的 ",
            "ICMP</span></var>:<var>%{item.name}</var>}}}%{mark?, 标记 <var%{mark.inv? ",
            r"data-tooltip=\"匹配除 %{mark.num}%{mark.mask? 带有掩码 %{mark.mask}} 的 ",
            r"fwmarks。\":%{mark.mask? data-tooltip=\"在比较前对fwmark 应用掩码 %",
            r"{mark.mask} 。\"}}>%{mark.val}</var>}%{dscp?, DSCP %{dscp.inv?<var data-",
            r"tooltip=\"匹配除 %{dscp.num?:%{dscp.name}} 以外的 DSCP 类型。\">%{dscp.val}</",
            "var>:<var>%{dscp.val}</var>}}%{helper?, 助手 %{helper.inv?<var data-",
            r"tooltip=\"匹配除 &quot;%{helper.name}&quot; 以外的任意助手。\">%{helper.val}",
            r"</var>:<var data-tooltip=\"%{helper.name}\">%{helper.val}</var>}}",
        ]

    def test_wrap_parenthesis_long(self):
        text = r"Must be required by a NotificationListenerService, to ensure that only the system can bind to it. See [url=https://developer.android.com/reference/android/Manifest.permission#BIND_NOTIFICATION_LISTENER_SERVICE]BIND_NOTIFICATION_LISTENER_SERVICE[/url]."
        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == [
            "Must be required by a NotificationListenerService, to ensure that only the ",
            "system can bind to it. See [url=https://developer.android.com/reference/",
            "android/",
            "Manifest.permission#BIND_NOTIFICATION_LISTENER_SERVICE]BIND_NOTIFICATION_LISTENER_SERVICE[/",
            "url].",
        ]

    def test_wrap_plural_form(self):
        text = r"Plural-Forms: nplurals=3; plural=n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2;\n"
        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == [
            "Plural-Forms: nplurals=3; plural=n%10==1 && n%100!=11 ? 0 : n%10>=2 && ",
            r"n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2;\n",
        ]

    def test_wrap_url(self):
        text = r"Language-Team: Ukrainian <https://mirror.git.trinitydesktop.org/weblate/projects/tdepim/kmail/uk/>\n"
        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == [
            "Language-Team: Ukrainian <https://mirror.git.trinitydesktop.org/weblate/",
            r"projects/tdepim/kmail/uk/>\n",
        ]

    def test_wrap_escape(self):
        text = r"x: to be continued with \"do not loop\", \"loop in current folder\", and \"loop in all folders\".\nWhen trying to find unread messages:"
        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == [
            r"x: to be continued with \"do not loop\", \"loop in current folder\", and ",
            r"\"loop in all folders\".\n",
            "When trying to find unread messages:",
        ]

    def test_wrap_label(self):
        text = r"You can get a copy of your Recovery Key by going to &syncBrand.shortName.label; Options on your other device, and selecting  \"My Recovery Key\" under \"Manage Account\"."
        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == [
            "You can get a copy of your Recovery Key by going to ",
            "&syncBrand.shortName.label; Options on your other device, and selecting  ",
            r"\"My Recovery Key\" under \"Manage Account\".",
        ]

    def test_wrap_wide_stop(self):
        text = "在 Mastodon 上关注 [@beeware@fosstodon.org](https://fosstodon.org/@beeware)，或[加入 BeeWare 爱好者邮件列表](/zh_CN/community/keep-informed/)以获取与项目相关的更新、提示、技巧和公告。"
        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == [
            "在 Mastodon 上关注 [@beeware@fosstodon.org](https://fosstodon.org/@beeware)，",
            "或[加入 BeeWare 爱好者邮件列表](/zh_CN/community/keep-informed/)以获取与项目",
            "相关的更新、提示、技巧和公告。",
        ]

    def test_wrap_escape_en(self):
        text = r"By default, \":doc:`Wire Transfer </applications/finance/payment_providers/wire_transfer>`\" is the only payment provider activated, but you still have to fill out the payment details."
        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == [
            r"By default, \":doc:`Wire Transfer </applications/finance/payment_providers/",
            r"wire_transfer>`\" is the only payment provider activated, but you still have ",
            "to fill out the payment details.",
        ]

    def test_wrap_escape_localized(self):
        text = r"기본값으로 \":doc:`온라인 이체 </applications/finance/payment_providers/wire_transfer>`\"만 결제대행업체을 사용하도록 설정되어 있으나, 여기에도 결제 세부 정보를 입력해야 합니다."
        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == [
            r"기본값으로 \":doc:`온라인 이체 </applications/finance/payment_providers/",
            r"wire_transfer>`\"만 결제대행업체을 사용하도록 설정되어 있으나, 여기에도 결제 ",
            r"세부 정보를 입력해야 합니다.",
        ]

    def test_wrap_limit(self):
        text = r"Ukuba uyayiqonda into eyenzekayo, \nungaxelela i-&brandShortName; ukuba iqalise ukuthemba ufaniso lwale sayithi. \n<b>Nokuba uyayithemba isayithi, le mposiso isenokuthetha ukuba   kukho umntu \nobhucabhuca ukudibanisa kwakho.</b>"
        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == [
            "Ukuba uyayiqonda into eyenzekayo, \\n",
            "ungaxelela i-&brandShortName; ukuba iqalise ukuthemba ufaniso lwale sayithi. ",
            "\\n",
            "<b>Nokuba uyayithemba isayithi, le mposiso isenokuthetha ukuba   kukho umntu ",
            "\\n",
            "obhucabhuca ukudibanisa kwakho.</b>",
        ]
