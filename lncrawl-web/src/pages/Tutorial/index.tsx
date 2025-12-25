import {
  BookOutlined,
  DeploymentUnitOutlined,
  FileDoneOutlined,
  FolderOpenOutlined,
  QuestionCircleOutlined,
  ReadOutlined,
  SafetyCertificateOutlined,
  SettingOutlined,
  UserOutlined,
} from '@ant-design/icons';
import type { CollapseProps, StepsProps } from 'antd';
import { Card, Collapse, Divider, Steps, Typography } from 'antd';
import { Link } from 'react-router-dom';

const { Title, Paragraph, Text } = Typography;

const steps: StepsProps['items'] = [
  {
    icon: <DeploymentUnitOutlined />,
    title: <Link to="/">Request Novel</Link>,
    description: 'Start by requesting a novel from a supported source',
    style: { flex: 1 },
  },
  {
    icon: <BookOutlined />,
    title: <Link to="/novels">Browse Novels</Link>,
    description: 'Browse the list of all collected novels',
    style: { flex: 1 },
  },
  {
    icon: <FolderOpenOutlined />,
    title: <Link to="/libraries">Organize Libraries</Link>,
    description: 'Create libraries to organize your novels',
    style: { flex: 1 },
  },
  {
    icon: <ReadOutlined />,
    title: 'Read & Download',
    description: 'Read novels online or download in various formats',
    style: { flex: 1 },
  },
];

const items: CollapseProps['items'] = [
  {
    key: 'getting-started',
    label: 'Getting Started',
    children: (
      <div>
        <Title level={4} style={{ marginTop: 0 }}>
          Welcome to Lightnovel Crawler!
        </Title>
        <Paragraph>
          This application helps you crawl, organize, and read light novels from
          various supported sources. Follow this guide to learn how to use all
          the features.
        </Paragraph>
        <Paragraph>
          <Text strong>Quick Start:</Text> Go to the{' '}
          <Link to="/">Requests page</Link> and paste a novel URL from a
          supported source to get started.
        </Paragraph>
      </div>
    ),
  },
  {
    key: 'request-novel',
    label: 'How to Request a Novel',
    children: (
      <div>
        <Title level={4} style={{ marginTop: 0 }}>
          <DeploymentUnitOutlined /> Requesting a Novel
        </Title>
        <Paragraph>
          To request a novel, you need a URL from one of the{' '}
          <Link to="/meta/sources">supported sources</Link>. Here's how:
        </Paragraph>
        <ol>
          <li>
            <Text strong>Find a novel:</Text> Browse any supported light novel
            website and find a novel you want to crawl.
          </li>
          <li>
            <Text strong>Copy the URL:</Text> Copy the URL of the novel's main
            page (usually the page that shows the novel's description and
            chapter list).
          </li>
          <li>
            <Text strong>Paste and submit:</Text> Go to the{' '}
            <Link to="/">Requests page</Link>, paste the URL in the input box,
            and click the submit button or press Enter.
          </li>
          <li>
            <Text strong>Wait for processing:</Text> The system will create a
            request to fetch the novel. You can monitor the progress on the
            request details page.
          </li>
        </ol>
        <Paragraph>
          <Text type="warning">
            Note: Make sure the URL is from a supported source. Check the{' '}
            <Link to="/meta/sources">Crawlers page</Link> to see all available
            sources.
          </Text>
        </Paragraph>
      </div>
    ),
  },
  {
    key: 'view-novels',
    label: 'Viewing and Managing Novels',
    children: (
      <div>
        <Title level={4} style={{ marginTop: 0 }}>
          <BookOutlined /> Novels Page
        </Title>
        <Paragraph>
          Once a novel has been successfully crawled, it will appear in the{' '}
          <Link to="/novels">Novels page</Link>. Browse all collected novels,
          use filters to search by title or source, and click any novel to view
          its details.
        </Paragraph>

        <Title level={5}>Novel Details Page</Title>
        <Paragraph>
          The novel details page contains three main sections:
        </Paragraph>
        <ul>
          <li>
            <Text strong>Novel Information:</Text> Cover image, title, author,
            description, tags, and action buttons (Refresh, Add to Library).
          </li>
          <li>
            <Text strong>Table of Contents:</Text> Volumes and chapters
            organized hierarchically. Click chapter titles to read, or use "Get"
            to fetch unavailable chapters. The "Download All" button fetches all
            content at once. Read chapters appear dimmed to track progress.
          </li>
          <li>
            <Text strong>Artifacts:</Text> View and download generated e-books
            (EPUB, PDF, MOBI, etc). Click "Make Artifact" to create downloadable
            files in your preferred formats.
          </li>
        </ul>

        <Title level={5}>Reading</Title>
        <Paragraph>
          Click any available chapter to open the built-in reader. Navigate
          between chapters using buttons or keyboard shortcuts. Customize your
          reading experience with theme, font, and text-to-speech settings.
          Enable auto-fetch in reader settings to automatically download
          chapters when needed.
        </Paragraph>
      </div>
    ),
  },
  {
    key: 'libraries',
    label: 'Creating and Using Libraries',
    children: (
      <div>
        <Title level={4} style={{ marginTop: 0 }}>
          <FolderOpenOutlined /> Libraries
        </Title>
        <Paragraph>
          Libraries help you organize your novels into collections. You can
          create multiple libraries for different purposes (e.g., "Favorites",
          "Reading", "Completed").
        </Paragraph>
        <Title level={5}>Creating a Library</Title>
        <ol>
          <li>
            Go to the <Link to="/libraries">Libraries page</Link>.
          </li>
          <li>Click the "Create Library" button.</li>
          <li>Enter a name and optional description for your library.</li>
          <li>Choose if you want the library to be public or private.</li>
          <li>Click "Create" to finish.</li>
        </ol>
        <Title level={5}>Adding Novels to Libraries</Title>
        <ol>
          <li>Navigate to a novel's details page.</li>
          <li>Click the "Add to Library" button.</li>
          <li>Select one or more libraries from the list.</li>
          <li>Click "Add" to confirm.</li>
        </ol>
        <Title level={5}>Managing Libraries</Title>
        <Paragraph>On the library details page, you can:</Paragraph>
        <ul>
          <li>View all novels in the library</li>
          <li>Edit the library name and description</li>
          <li>Remove novels from the library</li>
          <li>Delete the library (if you're the owner)</li>
        </ul>
      </div>
    ),
  },
  {
    key: 'reading',
    label: 'Reading Novels',
    children: (
      <div>
        <Title level={4} style={{ marginTop: 0 }}>
          <ReadOutlined /> Reading Novels
        </Title>
        <Paragraph>
          You can read novels directly in your browser using the built-in
          reader.
        </Paragraph>
        <Title level={5}>Opening the Reader</Title>
        <ol>
          <li>Go to a novel's details page.</li>
          <li>Click on any chapter from the chapter list.</li>
          <li>The reader will open in a new view.</li>
        </ol>
        <Title level={5}>Reader Features</Title>
        <ul>
          <li>
            <Text strong>Navigation:</Text> Use the navigation buttons or
            keyboard shortcuts to move between chapters.
          </li>
          <li>
            <Text strong>Settings:</Text> Click the settings icon to customize:
            <ul>
              <li>Theme (light/dark)</li>
              <li>Font family and size</li>
              <li>Line height</li>
              <li>Text-to-speech options</li>
            </ul>
          </li>
          <li>
            <Text strong>Table of Contents:</Text> Access the chapter list from
            within the reader.
          </li>
        </ul>
      </div>
    ),
  },
  {
    key: 'download',
    label: 'Downloading Novels',
    children: (
      <div>
        <Title level={4} style={{ marginTop: 0 }}>
          <FileDoneOutlined /> Downloading Artifacts
        </Title>
        <Paragraph>
          You can download novels in various formats for offline reading.
        </Paragraph>
        <Title level={5}>Creating Artifacts</Title>
        <ol>
          <li>Navigate to a novel's details page.</li>
          <li>Click the "Make Artifact" button.</li>
          <li>
            Select the format(s) you want:
            <ul>
              <li>EPUB - For e-readers and most reading apps</li>
              <li>PDF - For printing or PDF readers</li>
              <li>MOBI - For Kindle devices</li>
              <li>ZIP - Archive containing HTML files</li>
            </ul>
          </li>
          <li>Click "Create" to start the artifact generation job.</li>
          <li>Monitor the job progress and download when complete.</li>
        </ol>
        <Paragraph>
          <Text type="secondary">
            Tip: Artifact generation may take some time depending on the novel's
            size. You can check the job status from the job details page.
          </Text>
        </Paragraph>
      </div>
    ),
  },
  {
    key: 'settings',
    label: 'Settings and Preferences',
    children: (
      <div>
        <Title level={4} style={{ marginTop: 0 }}>
          <SettingOutlined /> Settings
        </Title>
        <Paragraph>
          Customize your experience by visiting the{' '}
          <Link to="/settings">Settings page</Link>.
        </Paragraph>
        <Title level={5}>Notification Settings</Title>
        <Paragraph>
          Configure email notifications for various events. Toggle each option
          on or off:
        </Paragraph>
        <ul>
          <li>
            <Text strong>On novel fetch request success:</Text> Receive an email
            when a novel has been successfully fetched and is ready to read.
          </li>
          <li>
            <Text strong>On artifact create request success:</Text> Get notified
            when an artifact (EPUB, PDF, MOBI, etc.) has been successfully
            generated and is ready for download.
          </li>
          <li>
            <Text strong>When any request starts running:</Text> Be notified
            when any job (novel fetch, artifact generation, etc.) begins
            processing.
          </li>
          <li>
            <Text strong>When any request is successful:</Text> Receive a
            notification whenever any job completes successfully.
          </li>
          <li>
            <Text strong>When any request failed:</Text> Get alerted when a job
            fails, so you can take action or retry.
          </li>
          <li>
            <Text strong>When any request canceled:</Text> Be notified if you or
            the system cancels a running job.
          </li>
        </ul>
        <Text type="warning">
          Note: You must verify your email first to receive notifications.
        </Text>

        <Title level={5}>Reader Settings</Title>
        <Paragraph>
          Customize your reading experience with these settings. They are saved
          as defaults and applied when you open the reader, but you can adjust
          them per session:
        </Paragraph>
        <ul>
          <li>
            <Text strong>Theme:</Text> Choose from various color schemes (light,
            dark, and other themes) for the reader background and text. Select
            the theme that's most comfortable for your eyes.
          </li>
          <li>
            <Text strong>Font Family:</Text> Select your preferred font from
            available options. Different fonts can improve readability based on
            your preference and device.
          </li>
          <li>
            <Text strong>Font Size:</Text> Adjust the text size using the +/-
            buttons. Increase for better visibility or decrease to fit more
            content on screen. Size is displayed in pixels.
          </li>
          <li>
            <Text strong>Line Height:</Text> Control the spacing between lines
            of text using a slider (range: 0.5 to 2.5). Higher values provide
            more breathing room, while lower values fit more text. Adjust based
            on your reading comfort.
          </li>
          <li>
            <Text strong>Voice:</Text> Select a text-to-speech voice from your
            browser's available voices. This enables the reader to read chapters
            aloud. Note: Requires browser support for speech synthesis.
          </li>
          <li>
            <Text strong>Pitch:</Text> Adjust the pitch of the text-to-speech
            voice using a slider (range: 0.1 to 2.0). Higher values make the
            voice sound higher-pitched, lower values make it deeper.
          </li>
          <li>
            <Text strong>Speed:</Text> Control how fast the text-to-speech voice
            reads using a slider (range: 0.1 to 2.0). Increase for faster
            reading or decrease for slower, more careful narration.
          </li>
          <li>
            <Text strong>Auto Download:</Text> When enabled, clicking on an
            unavailable chapter will automatically fetch its content and then
            open the reader. This streamlines the reading experience by
            eliminating manual chapter fetching.
          </li>
        </ul>
        <Paragraph>
          <Text type="secondary">
            Tip: Reader settings are saved automatically and persist across
            sessions. You can always override them temporarily while reading.
          </Text>
        </Paragraph>
      </div>
    ),
  },
  {
    key: 'profile',
    label: 'Profile and Email Verification',
    children: (
      <div>
        <Title level={4} style={{ marginTop: 0 }}>
          <UserOutlined /> Profile Page
        </Title>
        <Paragraph>
          Your <Link to="/profile">Profile page</Link> displays your account
          information: name (editable), email, role, tier, and join date. You
          can also manage your password and generate API tokens here.
        </Paragraph>

        <Title level={5} style={{ marginTop: 16 }}>
          Account Management
        </Title>
        <ul>
          <li>
            <Text strong>Change Name:</Text> Click "Edit" next to your name,
            enter a new display name (min 2 characters), and save.
          </li>
          <li>
            <Text strong>Change Password:</Text> Click "Change Password", enter
            your current and new password (min 6 characters), then update.
          </li>
          <li>
            <Text strong>Token:</Text> Generate tokens and share them with the
            new users for allowing them to signup.
          </li>
        </ul>

        <Title level={5} style={{ marginTop: 16 }}>
          <SafetyCertificateOutlined /> Email Verification
        </Title>
        <Paragraph>
          Verify your email to enable notifications and enhance account
          security. If unverified, you'll see a "Verify Email" button in the
          sidebar.
        </Paragraph>
        <ol>
          <li>Click "Verify Email" button.</li>
          <li>
            Check your email for a 6-digit code (check spam folder if needed).
          </li>
          <li>Enter the code in the verification modal.</li>
          <li>
            Click "Verify" to complete. Resend is available after 30 seconds.
          </li>
        </ol>
        <Paragraph>
          <Text type="secondary">
            Verified emails enable notifications (configure in{' '}
            <Link to="/settings">Settings</Link>), improve account security, and
            allow you to receive important updates.
          </Text>
        </Paragraph>
      </div>
    ),
  },
  {
    key: 'tips',
    label: 'Tips and Best Practices',
    children: (
      <div>
        <Title level={4} style={{ marginTop: 0 }}>
          Tips for Best Experience
        </Title>
        <ul>
          <li>
            <Text strong>Check supported sources:</Text> Before requesting a
            novel, make sure the source is supported. Visit the{' '}
            <Link to="/meta/sources">Crawlers page</Link> to see the full list.
          </li>
          <li>
            <Text strong>Use libraries:</Text> Organize your novels into
            libraries to keep track of what you're reading, want to read, or
            have completed.
          </li>
          <li>
            <Text strong>Monitor jobs:</Text> Keep an eye on your job list to
            see the status of novel requests and artifact generation.
          </li>
          <li>
            <Text strong>Refresh novels:</Text> If a novel has been updated on
            the source website, use the refresh button to update your local
            copy.
          </li>
          <li>
            <Text strong>Reader settings:</Text> Customize the reader to your
            preferences for the best reading experience.
          </li>
          <li>
            <Text strong>Feedback:</Text> Found a bug or have a suggestion? Use
            the <Link to="/feedbacks">Feedbacks page</Link> to report issues or
            share ideas.
          </li>
        </ul>
      </div>
    ),
  },
];

export const TutorialPage: React.FC<any> = () => {
  return (
    <>
      <Title level={2} style={{ marginTop: 0 }}>
        <QuestionCircleOutlined /> Tutorial
      </Title>

      <Card style={{ marginBottom: 24 }}>
        <Title level={4} style={{ marginTop: 0 }}>
          Quick Overview
        </Title>
        <Paragraph>
          Follow these steps to get started with Light Novel Crawler:
        </Paragraph>
        <Steps
          orientation="horizontal"
          items={steps}
          current={4}
          style={{ marginTop: 20 }}
          responsive
        />
      </Card>

      <Divider />

      <Title level={3}>Detailed Guide</Title>
      <Paragraph type="secondary" style={{ marginBottom: 16 }}>
        Expand the sections below to learn more about each feature.
      </Paragraph>

      <Collapse defaultActiveKey={['getting-started']} items={items} />
    </>
  );
};
