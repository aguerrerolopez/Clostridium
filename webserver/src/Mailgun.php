<?php
namespace App;

class Mailgun {
    /**
     * Send email
     *
     * @param string $to      Receiver address
     * @param string $subject Subject
     * @param string $message Message in plain-text
     */
    public static function sendEmail(string $to, string $subject, string $message): void {
        $domain = getenv('MAILGUN_DOMAIN') ?? '';
        $from = getenv('MAILGUN_FROM') ?? '';
        $apiKey = getenv('MAILGUN_APIKEY') ?? '';

        // Write to log instead if running in development
        if (empty($domain) || empty($from) || empty($apiKey)) {
            error_log("[EMAIL]To: $to\nSubject: $subject\n\n$message");
            return;
        }

        // Build HTML body
        $subject = htmlentities($subject);
        $message = str_replace("\n", "<br>\n", $message);
        $message = preg_replace('/https?:\/\/.+/', '<a href="$0" class="link">$0</a>', $message);
        $html = <<<HTML
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta http-equiv="X-UA-Compatible" content="IE=edge" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{$subject}</title>
<style type="text/css">
body {
    margin: 0;
    padding: 20px;
    background: #eff2f4;
    font-family: sans-serif;
}
.container {
    background: #fff;
    margin: 0 auto;
    padding: 20px;
    max-width: 600px;
    border-spacing: 0;
    color: #000;
    font-size: 16px;
    line-height: 1.4;
}
a.link,
a.link:visited {
    color: #154260;
    word-wrap: break-word;
}
</style>
</head>
<body>
    <div class="container">{$message}</table>
</body>
</html>
HTML;

        // Send email
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, "https://api.mailgun.net/v3/$domain/messages");
        curl_setopt($ch, CURLOPT_HTTPAUTH, CURLAUTH_BASIC);
        curl_setopt($ch, CURLOPT_USERPWD, "api:$apiKey");
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 10);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, [
            'from'    => APP_NAME . " <$from>",
            'to'      => $to,
            'subject' => $subject,
            'html'    => $html,
        ]);
        curl_exec($ch);
        curl_close($ch);
        unset($ch);
    }
}
