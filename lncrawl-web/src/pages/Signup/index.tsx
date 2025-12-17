import { store } from '@/store';
import { Auth } from '@/store/_auth';
import { stringifyError } from '@/utils/errors';
import { LeftOutlined, LoginOutlined } from '@ant-design/icons';
import {
  Alert,
  Button,
  Checkbox,
  Divider,
  Flex,
  Form,
  Input,
  Modal,
  Typography,
} from 'antd';
import FormItem from 'antd/es/form/FormItem';
import axios from 'axios';
import { useState } from 'react';
import './policy-content.scss';

export const SignupPage: React.FC<any> = () => {
  const [form] = Form.useForm();
  const [error, setError] = useState<string>();
  const [loading, setLoading] = useState<boolean>(false);
  const [privacyModalOpen, setPrivacyModalOpen] = useState<boolean>(false);
  const [termsModalOpen, setTermsModalOpen] = useState<boolean>(false);
  const [privacyContent, setPrivacyContent] = useState<string>('');
  const [termsContent, setTermsContent] = useState<string>('');
  const [loadingPrivacy, setLoadingPrivacy] = useState<boolean>(false);
  const [loadingTerms, setLoadingTerms] = useState<boolean>(false);

  const handleSignup = async (data: any) => {
    setLoading(true);
    setError(undefined);
    try {
      const result = await axios.post(`/api/auth/signup`, data);
      store.dispatch(Auth.action.login(result.data));
    } catch (err) {
      setError(stringifyError(err, 'Oops! Something went wrong.'));
    } finally {
      setLoading(false);
    }
  };

  const loadPrivacyPolicy = async () => {
    if (privacyContent) {
      setPrivacyModalOpen(true);
      return;
    }
    setLoadingPrivacy(true);
    try {
      const response = await fetch('/PRIVACY_POLICY.html');
      if (!response.ok) {
        throw new Error(`Failed to load: ${response.statusText}`);
      }
      const html = await response.text();
      setPrivacyContent(html);
      setPrivacyModalOpen(true);
    } catch (err) {
      setError('Failed to load privacy policy. Please try again later.');
      console.error('Error loading privacy policy:', err);
    } finally {
      setLoadingPrivacy(false);
    }
  };

  const loadTermsOfService = async () => {
    if (termsContent) {
      setTermsModalOpen(true);
      return;
    }
    setLoadingTerms(true);
    try {
      const response = await fetch('/TERMS_OF_SERVICE.html');
      if (!response.ok) {
        throw new Error(`Failed to load: ${response.statusText}`);
      }
      const html = await response.text();
      setTermsContent(html);
      setTermsModalOpen(true);
    } catch (err) {
      setError('Failed to load terms of service. Please try again later.');
      console.error('Error loading terms of service:', err);
    } finally {
      setLoadingTerms(false);
    }
  };

  return (
    <Form
      form={form}
      onFinish={handleSignup}
      size="large"
      layout="vertical"
      labelCol={{ style: { padding: 0 } }}
    >
      <Form.Item
        name="name"
        label="Full Name"
        rules={[
          {
            validator: (_, value) =>
              value && value.trim().length >= 2
                ? Promise.resolve()
                : Promise.reject('Please enter a valid name'),
          },
        ]}
      >
        <Input placeholder="Enter full name" autoComplete="name" />
      </Form.Item>

      <Form.Item
        name="email"
        label="Email"
        rules={[
          { required: true, message: 'Please enter your email' },
          { type: 'email', message: 'Please enter a valid email' },
        ]}
      >
        <Input placeholder="Enter email" autoComplete="new-user" />
      </Form.Item>

      <Form.Item
        name={'password'}
        label="Password"
        rules={[
          { required: true, message: 'Please enter a password' },
          { min: 6, message: 'Password must be at least 6 characters' },
        ]}
        hasFeedback
      >
        <Input.Password
          placeholder="New password"
          autoComplete="new-password"
        />
      </Form.Item>

      <Form.Item
        name="referrer"
        label="Referrer Token"
        rules={[{ required: true, message: 'Please enter a referrer token' }]}
      >
        <Input
          placeholder="Enter referrer token"
          autoComplete="referrer-token"
        />
      </Form.Item>

      <Typography.Text type="secondary" style={{ fontSize: 12 }}>
        Registration is now referral-only. If you want to refer someone, you can
        find your referral token on your Profile page.
      </Typography.Text>

      <Form.Item
        name="acceptTerms"
        valuePropName="checked"
        rules={[
          {
            validator: (_, value) =>
              value
                ? Promise.resolve()
                : Promise.reject(
                    'You must accept the Privacy Policy and Terms of Service to continue'
                  ),
          },
        ]}
      >
        <Checkbox>
          I accept the{' '}
          <Typography.Link
            onClick={(e) => {
              e.preventDefault();
              loadPrivacyPolicy();
            }}
            style={{ padding: 0 }}
          >
            Privacy Policy
          </Typography.Link>{' '}
          and{' '}
          <Typography.Link
            onClick={(e) => {
              e.preventDefault();
              loadTermsOfService();
            }}
            style={{ padding: 0 }}
          >
            Terms of Service
          </Typography.Link>
        </Checkbox>
      </Form.Item>

      {Boolean(error) && (
        <Alert
          type="warning"
          showIcon
          message={error}
          closable
          onClose={() => setError('')}
        />
      )}
      <FormItem style={{ marginTop: '20px' }}>
        <Button
          block
          type="primary"
          htmlType="submit"
          loading={loading}
          disabled={loading}
          icon={<LoginOutlined />}
          children={'Register'}
        />
      </FormItem>

      <Divider />
      <Flex justify="center">
        <Typography.Link href="/login">
          <LeftOutlined /> Back to login
        </Typography.Link>
      </Flex>

      <Modal
        title="Privacy Policy"
        open={privacyModalOpen}
        onCancel={() => setPrivacyModalOpen(false)}
        footer={[
          <Button key="close" onClick={() => setPrivacyModalOpen(false)}>
            Close
          </Button>,
        ]}
        width={800}
        style={{ top: 20 }}
      >
        <div
          style={{
            maxHeight: '70vh',
            overflowY: 'auto',
            padding: '16px 0',
          }}
        >
          {loadingPrivacy ? (
            <Typography.Text>Loading...</Typography.Text>
          ) : (
            <div
              className="policy-content"
              dangerouslySetInnerHTML={{ __html: privacyContent }}
              style={{
                lineHeight: '1.6',
              }}
            />
          )}
        </div>
      </Modal>

      <Modal
        title="Terms of Service"
        open={termsModalOpen}
        onCancel={() => setTermsModalOpen(false)}
        footer={[
          <Button key="close" onClick={() => setTermsModalOpen(false)}>
            Close
          </Button>,
        ]}
        width={800}
        style={{ top: 20 }}
      >
        <div
          style={{
            maxHeight: '70vh',
            overflowY: 'auto',
            padding: '16px 0',
          }}
        >
          {loadingTerms ? (
            <Typography.Text>Loading...</Typography.Text>
          ) : (
            <div
              className="policy-content"
              dangerouslySetInnerHTML={{ __html: termsContent }}
              style={{
                lineHeight: '1.6',
              }}
            />
          )}
        </div>
      </Modal>
    </Form>
  );
};
