from __future__ import absolute_import

from django.core.urlresolvers import reverse

from sentry.models import Organization, OrganizationMemberTeam
from sentry.testutils import APITestCase


class CreateOrganizationMemberTeamTest(APITestCase):
    def test_can_join_as_owner_without_open_membership(self):
        organization = self.create_organization(
            name='foo',
            owner=self.user,
            flags=0,
        )
        team = self.create_team(name='foo', organization=organization)
        user = self.create_user('dummy@example.com')
        member_om = self.create_member(
            organization=organization,
            user=user,
            role='owner',
            teams=[],
        )

        path = reverse('sentry-api-0-organization-member-team-details', args=[
            organization.slug, member_om.id, team.slug,
        ])

        self.login_as(user)

        resp = self.client.post(path)

        assert resp.status_code == 201

    def test_cannot_join_as_member_without_open_membership(self):
        organization = self.create_organization(
            name='foo',
            owner=self.user,
            flags=0,
        )
        team = self.create_team(name='foo', organization=organization)
        user = self.create_user('dummy@example.com')
        member_om = self.create_member(
            organization=organization,
            user=user,
            role='member',
            teams=[],
        )

        path = reverse('sentry-api-0-organization-member-team-details', args=[
            organization.slug, member_om.id, team.slug,
        ])

        self.login_as(user)

        resp = self.client.post(path)

        assert resp.status_code == 202

        assert not OrganizationMemberTeam.objects.filter(
            team=team,
            organizationmember=member_om,
        ).exists()

    def test_can_join_as_member_with_open_membership(self):
        organization = self.create_organization(
            name='foo',
            owner=self.user,
            flags=Organization.flags.allow_joinleave,
        )
        team = self.create_team(name='foo', organization=organization)
        user = self.create_user('dummy@example.com')
        member_om = self.create_member(
            organization=organization,
            user=user,
            role='member',
            teams=[],
        )

        path = reverse('sentry-api-0-organization-member-team-details', args=[
            organization.slug, member_om.id, team.slug,
        ])

        self.login_as(user)

        resp = self.client.post(path)

        assert resp.status_code == 201

        omt = OrganizationMemberTeam.objects.get(
            team=team,
            organizationmember=member_om,
        )
        assert omt.is_active


class DeleteOrganizationMemberTeamTest(APITestCase):
    def test_can_leave_as_member(self):
        organization = self.create_organization(name='foo', owner=self.user)
        team = self.create_team(name='foo', organization=organization)
        user = self.create_user('dummy@example.com')
        member_om = self.create_member(
            organization=organization,
            user=user,
            role='member',
            teams=[team],
        )

        path = reverse('sentry-api-0-organization-member-team-details', args=[
            organization.slug, member_om.id, team.slug,
        ])

        self.login_as(user)

        resp = self.client.delete(path)

        assert resp.status_code == 200

        assert OrganizationMemberTeam.objects.filter(
            team=team,
            organizationmember=member_om,
            is_active=False,
        ).exists()

    def test_can_leave_as_non_member(self):
        organization = self.create_organization(name='foo', owner=self.user)
        team = self.create_team(name='foo', organization=organization)
        user = self.create_user('dummy@example.com')
        member_om = self.create_member(
            organization=organization,
            user=user,
            role='member',
            teams=[],
        )

        path = reverse('sentry-api-0-organization-member-team-details', args=[
            organization.slug, member_om.id, team.slug,
        ])

        self.login_as(user)

        resp = self.client.delete(path)

        assert resp.status_code == 200

        assert not OrganizationMemberTeam.objects.filter(
            team=team,
            organizationmember=member_om,
            is_active=True,
        ).exists()
